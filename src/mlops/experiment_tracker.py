"""Log a model training run to MLflow — parameters, metrics, artifacts, tags."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import mlflow
import mlflow.sklearn

from src.mlops.mlflow_client import setup_mlflow

_ROOT = Path(__file__).resolve().parents[2]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_ROOT),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def log_training_run(
    model,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    feature_columns: list,
    artifact_path: Optional[str] = None,
    drift_status: Optional[str] = None,
    bias_summary: Optional[dict] = None,
    run_name: Optional[str] = None,
) -> str:
    """Log a full training run. Returns the MLflow run_id."""
    setup_mlflow()

    with mlflow.start_run(run_name=run_name or "training_run") as run:
        # Parameters
        mlflow.log_params(params)
        mlflow.log_param("feature_count", len(feature_columns))
        mlflow.log_param("git_commit", _git_commit())
        if drift_status:
            mlflow.log_param("drift_status_at_training", drift_status)

        # Metrics
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(k, v)

        # Tags
        mlflow.set_tag("model_type", type(model).__name__)
        mlflow.set_tag("phase", "Phase 03")
        if drift_status:
            mlflow.set_tag("drift_triggered", drift_status == "high")

        # Feature list as artifact
        feat_path = _ROOT / "data" / "reports" / "feature_columns.json"
        feat_path.parent.mkdir(parents=True, exist_ok=True)
        feat_path.write_text(json.dumps(feature_columns, indent=2))
        mlflow.log_artifact(str(feat_path), artifact_path="features")

        # Bias summary if present
        if bias_summary:
            bias_path = _ROOT / "data" / "reports" / "mlflow_bias_summary.json"
            bias_path.write_text(json.dumps(bias_summary, indent=2, default=str))
            mlflow.log_artifact(str(bias_path), artifact_path="reports")

        # Model artifact
        if model is not None:
            mlflow.sklearn.log_model(model, artifact_path="model")

        # Log the joblib artifact path as param if provided
        if artifact_path:
            mlflow.log_param("artifact_path", artifact_path)

        return run.info.run_id


def get_latest_run() -> Optional[Dict[str, Any]]:
    """Return the latest MLflow run as a dict, or None if no runs exist."""
    setup_mlflow()
    try:
        runs = mlflow.search_runs(order_by=["start_time DESC"])
        if runs.empty:
            return None
        row = runs.iloc[0]
        return {
            "run_id": row["run_id"],
            "status": row["status"],
            "start_time": str(row["start_time"]),
            "metrics": {k.replace("metrics.", ""): v for k, v in row.items() if k.startswith("metrics.")},
            "params": {k.replace("params.", ""): v for k, v in row.items() if k.startswith("params.")},
        }
    except Exception:
        return None
