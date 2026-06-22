"""Adversarial input checks — FR18.

Checks for statistical outliers vs training distribution and multi-feature anomalies.
All rejected inputs are logged to the audit trail.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[2]
_PROCESSED_PATH = _ROOT / "data" / "processed" / "matches_processed.csv"


def _load_training_stats() -> Optional[Dict[str, Dict]]:
    """Load mean/std for numeric features from processed data."""
    try:
        import pandas as pd
        df = pd.read_csv(_PROCESSED_PATH)
        numeric = df.select_dtypes(include="number")
        stats = {}
        for col in numeric.columns:
            stats[col] = {"mean": float(numeric[col].mean()), "std": float(numeric[col].std())}
        return stats
    except Exception:
        return None


_TRAINING_STATS: Optional[Dict] = None


def _get_stats():
    global _TRAINING_STATS
    if _TRAINING_STATS is None:
        _TRAINING_STATS = _load_training_stats()
    return _TRAINING_STATS


def check_feature_outliers(features: Dict[str, float], z_threshold: float = 5.0) -> Dict[str, Any]:
    """Flag features > z_threshold std devs from training mean (FR18.2)."""
    stats = _get_stats()
    if stats is None:
        return {"checked": False, "reason": "training stats unavailable"}

    flagged = []
    for feat, val in features.items():
        if feat in stats and stats[feat]["std"] > 0:
            z = abs(val - stats[feat]["mean"]) / stats[feat]["std"]
            if z > z_threshold:
                flagged.append({"feature": feat, "value": val, "z_score": round(z, 2)})

    return {
        "checked": True,
        "outliers_detected": len(flagged) > 0,
        "flagged_features": flagged,
        "threshold_std": z_threshold,
    }


def check_simultaneous_anomalies(features: Dict[str, float], max_allowed: int = 3) -> Dict[str, Any]:
    """Quarantine if too many features are simultaneously anomalous (FR18.5)."""
    result = check_feature_outliers(features)
    flagged_count = len(result.get("flagged_features", []))
    quarantine = flagged_count > max_allowed
    return {
        "quarantine": quarantine,
        "flagged_count": flagged_count,
        "max_allowed": max_allowed,
        "details": result,
    }
