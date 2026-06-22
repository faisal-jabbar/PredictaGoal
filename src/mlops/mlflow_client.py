"""MLflow client initialisation — local file-based tracking by default."""

import os
from pathlib import Path

import mlflow

_EXPERIMENT_NAME = "predictagoal_football_predictions"
_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_tracking_uri() -> str:
    if _TRACKING_URI:
        return _TRACKING_URI
    # Use file:// URI so MLflow accepts the path on all platforms
    local_path = _PROJECT_ROOT / "mlruns"
    local_path.mkdir(parents=True, exist_ok=True)
    return local_path.as_uri()


def setup_mlflow() -> str:
    """Configure MLflow tracking URI and create experiment. Returns experiment id."""
    uri = get_tracking_uri()
    mlflow.set_tracking_uri(uri)
    try:
        exp = mlflow.get_experiment_by_name(_EXPERIMENT_NAME)
        if exp is None:
            exp_id = mlflow.create_experiment(_EXPERIMENT_NAME)
        else:
            exp_id = exp.experiment_id
        mlflow.set_experiment(_EXPERIMENT_NAME)
        return exp_id
    except Exception as e:
        return f"error:{e}"


def get_experiment_name() -> str:
    return _EXPERIMENT_NAME
