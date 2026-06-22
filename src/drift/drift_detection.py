"""
FR12 — Drift Detection (reporting only).
Compares feature distributions between baseline and recent periods.
Auto-retraining is Phase 03 — this module only detects and reports.
"""
import os
from datetime import datetime
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from scipy import stats

from src.config import settings
from src.database import firestore_service
from src.features.feature_engineering import FEATURE_COLS
from src.utils.file_utils import save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

DRIFT_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "drift_report.json")

# Fraction used as the "recent" window
RECENT_FRACTION = 0.20
# PSI threshold for drift
PSI_LOW = 0.10
PSI_MEDIUM = 0.20
PSI_HIGH = 0.25


def _psi(baseline: np.ndarray, recent: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index between two distributions."""
    all_vals = np.concatenate([baseline, recent])
    min_val, max_val = all_vals.min(), all_vals.max()
    if min_val == max_val:
        return 0.0

    bin_edges = np.linspace(min_val, max_val, bins + 1)
    base_counts, _ = np.histogram(baseline, bins=bin_edges)
    recent_counts, _ = np.histogram(recent, bins=bin_edges)

    base_pct = base_counts / (len(baseline) + 1e-10) + 1e-6
    recent_pct = recent_counts / (len(recent) + 1e-10) + 1e-6

    psi = float(np.sum((recent_pct - base_pct) * np.log(recent_pct / base_pct)))
    return round(abs(psi), 4)


def _ks_test(baseline: np.ndarray, recent: np.ndarray) -> Dict[str, Any]:
    stat, p_value = stats.ks_2samp(baseline, recent)
    return {"ks_statistic": round(float(stat), 4), "p_value": round(float(p_value), 4)}


def _drift_level(psi: float) -> str:
    if psi < PSI_LOW:
        return "none"
    elif psi < PSI_MEDIUM:
        return "low"
    elif psi < PSI_HIGH:
        return "medium"
    return "high"


def run_drift_report(features_df: pd.DataFrame) -> Dict[str, Any]:
    df = features_df.dropna(subset=FEATURE_COLS).sort_values("date").reset_index(drop=True)
    n = len(df)
    split = int(n * (1 - RECENT_FRACTION))

    baseline_df = df.iloc[:split]
    recent_df = df.iloc[split:]

    log.info(f"Drift detection: baseline={len(baseline_df)}, recent={len(recent_df)}")

    feature_results = []
    drifted = []

    for col in FEATURE_COLS:
        base_vals = baseline_df[col].values.astype(float)
        rec_vals = recent_df[col].values.astype(float)

        psi = _psi(base_vals, rec_vals)
        ks = _ks_test(base_vals, rec_vals)
        level = _drift_level(psi)

        feature_results.append({
            "feature": col,
            "psi": psi,
            "drift_level": level,
            "ks_statistic": ks["ks_statistic"],
            "ks_p_value": ks["p_value"],
            "baseline_mean": round(float(base_vals.mean()), 4),
            "recent_mean": round(float(rec_vals.mean()), 4),
            "mean_shift": round(float(rec_vals.mean() - base_vals.mean()), 4),
        })

        if level in ("medium", "high"):
            drifted.append(col)

    max_psi = max(r["psi"] for r in feature_results)
    overall_level = _drift_level(max_psi)

    report = {
        "baseline_period": {
            "from": str(baseline_df["date"].min().date()),
            "to": str(baseline_df["date"].max().date()),
            "rows": int(len(baseline_df)),
        },
        "recent_period": {
            "from": str(recent_df["date"].min().date()),
            "to": str(recent_df["date"].max().date()),
            "rows": int(len(recent_df)),
        },
        "features_checked": len(FEATURE_COLS),
        "drifted_features": drifted,
        "drifted_count": len(drifted),
        "overall_drift_level": overall_level,
        "max_psi": round(max_psi, 4),
        "feature_details": feature_results,
        "notes": (
            "This is a Phase 02 drift detection report using PSI and KS-test. "
            "Auto-retraining on detected drift is a Phase 03 feature."
        ),
        "generated_at": datetime.utcnow().isoformat(),
    }

    save_json(report, DRIFT_REPORT_PATH)
    log.info(f"Drift report saved: {DRIFT_REPORT_PATH} — overall level: {overall_level}")

    # Firestore-safe version (no nested arrays/lists)
    safe_report = {k: v for k, v in report.items() if k != "feature_details"}
    safe_report["drifted_features"] = ", ".join(drifted) if drifted else "none"
    firestore_service.write_document(
        "drift_reports", "latest", safe_report, fallback_path=DRIFT_REPORT_PATH
    )

    return report
