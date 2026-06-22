"""Reliability checks — verify model artifact and feature columns before inference."""

from pathlib import Path
from typing import Dict, Any

_ROOT = Path(__file__).resolve().parents[2]
_MODEL_PATH    = _ROOT / "models" / "artifacts" / "football_match_model.joblib"
_FEATURES_PATH = _ROOT / "models" / "artifacts" / "feature_columns.json"


def check_model_ready() -> Dict[str, Any]:
    """Verify model artifact and feature columns exist before inference."""
    model_ok    = _MODEL_PATH.exists()
    features_ok = _FEATURES_PATH.exists()
    ready = model_ok and features_ok
    return {
        "ready": ready,
        "model_artifact": str(_MODEL_PATH),
        "model_exists": model_ok,
        "features_artifact": str(_FEATURES_PATH),
        "features_exists": features_ok,
        "error": None if ready else "Model or feature columns artifact missing. Run script 07.",
    }
