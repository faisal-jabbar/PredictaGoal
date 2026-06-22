"""Model promotion logic — runs after retraining to decide if new model replaces champion."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from src.orchestration.retraining_decision import evaluate_promotion
from src.mlops.model_versioning import write_version_record, read_version_record
from src.mlops.model_registry import register_model
from src.audit import audit_service
from src.database import firestore_service

_ROOT = Path(__file__).resolve().parents[2]
_MODEL_REPORT = _ROOT / "models" / "reports" / "model_training_report.json"


def _load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return None


def run_promotion_check(
    candidate_model,
    candidate_accuracy: float,
    candidate_draw_f1: float,
    feature_columns: list,
    artifact_path: str,
    mlflow_run_id: str = None,
) -> Dict[str, Any]:
    """Evaluate and possibly promote a candidate model. Returns promotion report."""
    current = read_version_record() or {}
    current_accuracy = current.get("accuracy", 0.0)
    current_draw_f1  = current.get("draw_f1", 0.0)

    from pathlib import Path as _P
    candidate_saved = _P(artifact_path).exists() if artifact_path else False

    decision = evaluate_promotion(
        candidate_accuracy, candidate_draw_f1,
        current_accuracy, current_draw_f1,
        candidate_saved,
    )

    if decision["promote"]:
        version_record = write_version_record(
            accuracy=candidate_accuracy,
            draw_f1=candidate_draw_f1,
            feature_columns=feature_columns,
            artifact_path=artifact_path,
            promoted=True,
            mlflow_run_id=mlflow_run_id,
        )
        register_model(version_record)
        audit_service.log("model_promotion", {"version": version_record.get("model_version"), **decision})
    else:
        audit_service.log("model_promotion", {"promoted": False, **decision})

    return {**decision, "promotion_attempted_at": datetime.now(timezone.utc).isoformat()}
