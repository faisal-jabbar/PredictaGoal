"""Retraining decision logic — reads drift report and model report, decides whether to retrain.

Triggers retraining if ANY of:
  - overall_drift_level == "high"
  - max_psi >= 0.25
  - manual_force_retrain == True

Promotes candidate only if:
  - candidate_accuracy >= current_accuracy - 0.01
  - candidate_draw_f1 >= current_draw_f1 - 0.02
  - candidate model saved successfully
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.database import firestore_service

_ROOT = Path(__file__).resolve().parents[2]
_DRIFT_REPORT = _ROOT / "data" / "reports" / "drift_report.json"
_MODEL_REPORT  = _ROOT / "models" / "reports" / "model_training_report.json"
_DECISION_PATH = _ROOT / "data" / "reports" / "retraining_decision.json"

# Config thresholds
PSI_RETRAIN_THRESHOLD   = 0.25
ACCURACY_DROP_TOLERANCE = 0.01   # candidate must be >= current - 0.01
DRAW_F1_DROP_TOLERANCE  = 0.02


def _load_json(path: Path) -> Optional[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return None


def evaluate_retraining_need(force: bool = False) -> Dict[str, Any]:
    """Read drift and model reports. Return decision dict."""
    drift = _load_json(_DRIFT_REPORT) or {}
    model = _load_json(_MODEL_REPORT) or {}

    overall_drift = drift.get("overall_drift_level", "none")
    max_psi       = drift.get("max_psi", 0.0)
    drifted       = drift.get("drifted_features", [])

    reasons = []
    if force:
        reasons.append("manual_force_retrain=True")
    if overall_drift == "high":
        reasons.append(f"overall_drift_level=high")
    if max_psi >= PSI_RETRAIN_THRESHOLD:
        reasons.append(f"max_psi={max_psi:.4f} >= {PSI_RETRAIN_THRESHOLD}")

    should_retrain = bool(reasons)

    decision = {
        "should_retrain": should_retrain,
        "reasons": reasons,
        "overall_drift_level": overall_drift,
        "max_psi": max_psi,
        "drifted_features": drifted,
        "force_requested": force,
        "current_model_accuracy": model.get("test_accuracy"),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "status": "retrain_needed" if should_retrain else "no_retrain_needed",
    }

    _DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DECISION_PATH.write_text(json.dumps(decision, indent=2, default=str))

    try:
        firestore_service.write_document("retraining_decisions", "latest", decision)
    except Exception:
        pass

    return decision


def evaluate_promotion(
    candidate_accuracy: float,
    candidate_draw_f1: float,
    current_accuracy: float,
    current_draw_f1: float,
    candidate_saved: bool,
) -> Dict[str, Any]:
    """Decide whether to promote a candidate model."""
    checks = {
        "accuracy_ok": candidate_accuracy >= current_accuracy - ACCURACY_DROP_TOLERANCE,
        "draw_f1_ok":  candidate_draw_f1  >= current_draw_f1  - DRAW_F1_DROP_TOLERANCE,
        "artifact_ok": candidate_saved,
    }
    promote = all(checks.values())

    return {
        "promote": promote,
        "checks": checks,
        "candidate_accuracy": candidate_accuracy,
        "candidate_draw_f1":  candidate_draw_f1,
        "current_accuracy":   current_accuracy,
        "current_draw_f1":    current_draw_f1,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
