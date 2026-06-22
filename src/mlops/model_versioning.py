"""Model version metadata — creates and reads version records."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import subprocess

_ROOT = Path(__file__).resolve().parents[2]
_VERSION_PATH = _ROOT / "models" / "reports" / "model_version.json"
_REGISTRY_PATH = _ROOT / "data" / "reports" / "model_registry_report.json"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_ROOT),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def _make_version_tag() -> str:
    now = datetime.now(timezone.utc)
    return f"v{now.strftime('%Y.%m.%d.%H%M')}"


def write_version_record(
    accuracy: float,
    draw_f1: float,
    feature_columns: list,
    artifact_path: str,
    model_type: str = "RandomForestClassifier",
    status: str = "active",
    promoted: bool = True,
    mlflow_run_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Write model_version.json and model_registry_report.json."""
    _VERSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "model_version": _make_version_tag(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "model_type": model_type,
        "accuracy": round(accuracy, 4),
        "draw_f1": round(draw_f1, 4),
        "feature_columns": feature_columns,
        "artifact_path": artifact_path,
        "status": status,
        "promoted": promoted,
        "mlflow_run_id": mlflow_run_id,
    }
    if extra:
        record.update(extra)

    _VERSION_PATH.write_text(json.dumps(record, indent=2))
    _REGISTRY_PATH.write_text(json.dumps(record, indent=2))

    return record


def read_version_record() -> Optional[Dict[str, Any]]:
    if _VERSION_PATH.exists():
        return json.loads(_VERSION_PATH.read_text())
    return None
