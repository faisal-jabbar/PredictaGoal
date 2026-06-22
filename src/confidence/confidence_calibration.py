"""
FR11 — Prediction Confidence Calibration.
Derives a Prediction Confidence Score (PCS) from model output probabilities.
Does NOT fake confidence — every value is derived from actual predictions.

Formula:
  margin_score = (max_prob - 1/n) / (1 - 1/n)
  This measures how far the leading probability is from a uniform baseline,
  scaled to [0,1] where 1.0 means certainty and 0.0 means perfectly uniform.
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import numpy as np

from src.config import settings
from src.database import firestore_service
from src.utils.file_utils import save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

CONFIDENCE_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "confidence_report.json")

N_CLASSES = 3
UNIFORM_PROB = 1.0 / N_CLASSES      # 0.333...

# Tier thresholds (on margin_score)
TIER_HIGH     = 0.45   # max_prob ≈ 0.63+
TIER_MEDIUM   = 0.25   # max_prob ≈ 0.50+
TIER_LOW      = 0.10   # max_prob ≈ 0.40+


def _margin_score(probs: List[float]) -> float:
    """
    How far the leading probability is from a uniform baseline,
    normalised to [0, 1].
    """
    max_p = max(probs)
    score = (max_p - UNIFORM_PROB) / (1.0 - UNIFORM_PROB)
    return float(round(max(0.0, score), 4))


def _entropy(probs: List[float]) -> float:
    p = np.array([max(x, 1e-10) for x in probs])
    return float(-np.sum(p * np.log(p)))


def _top2_margin(probs: List[float]) -> float:
    sorted_p = sorted(probs, reverse=True)
    return float(round(sorted_p[0] - sorted_p[1], 4))


def _feature_completeness_penalty(feature_values: Optional[Dict[str, float]]) -> float:
    if feature_values is None:
        return 0.0
    total = len(feature_values)
    if total == 0:
        return 0.0
    zero_count = sum(1 for v in feature_values.values() if v == 0.0)
    return round(min(zero_count / total * 0.10, 0.10), 4)


def calculate_pcs(
    probabilities: Dict[str, float],
    feature_values: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    probs = list(probabilities.values())
    margin = _margin_score(probs)
    top2_gap = _top2_margin(probs)
    raw_entropy = _entropy(probs)
    penalty = _feature_completeness_penalty(feature_values)

    # PCS blends margin score (80%) and top-2 gap (20%), minus penalty
    pcs_raw = 0.80 * margin + 0.20 * min(top2_gap / 0.5, 1.0)
    pcs = float(round(max(0.0, pcs_raw - penalty), 4))

    tier, note = _assign_tier(pcs, probabilities)

    return {
        "pcs": pcs,
        "confidence_tier": tier,
        "confidence_note": note,
        "margin_score": margin,
        "top2_margin": top2_gap,
        "entropy": round(raw_entropy, 4),
        "feature_penalty": penalty,
        "probabilities": probabilities,
    }


def _assign_tier(pcs: float, probs: Dict[str, float]) -> tuple:
    max_prob = max(probs.values())
    if pcs >= TIER_HIGH:
        return "HIGH", (
            f"High confidence. The leading outcome probability is {max_prob:.1%}, "
            "well above the 33% random baseline."
        )
    elif pcs >= TIER_MEDIUM:
        return "MEDIUM", (
            f"Moderate confidence. The leading outcome ({max_prob:.1%}) shows a meaningful edge, "
            "but uncertainty remains."
        )
    elif pcs >= TIER_LOW:
        return "LOW", (
            f"Low confidence. The leading probability is {max_prob:.1%} — a slight lean, "
            "but the outcome probabilities are close. Treat this prediction with caution."
        )
    else:
        return "UNRELIABLE", (
            f"Very low confidence. The probability distribution is nearly uniform (max: {max_prob:.1%}). "
            "The model has insufficient historical signal to differentiate outcomes for this matchup."
        )


def run_confidence_report(
    sample_prediction: Dict[str, Any],
    feature_values: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    probs = sample_prediction.get("probabilities", {})
    result = calculate_pcs(probs, feature_values)

    report = {
        "match": f"{sample_prediction.get('home_team')} vs {sample_prediction.get('away_team')}",
        "match_date": sample_prediction.get("match_date"),
        "prediction": sample_prediction.get("prediction"),
        **result,
        "generated_at": datetime.utcnow().isoformat(),
    }

    save_json(report, CONFIDENCE_REPORT_PATH)
    log.info(f"Confidence report saved: {CONFIDENCE_REPORT_PATH}")

    firestore_service.write_document(
        "confidence_reports",
        "latest",
        report,
        fallback_path=CONFIDENCE_REPORT_PATH,
    )

    return report
