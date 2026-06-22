"""Model registry — reads/writes model version records and Firestore."""

import json
from pathlib import Path
from typing import Optional

from src.mlops.model_versioning import read_version_record
from src.database import firestore_service

_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "reports" / "model_registry_report.json"


def get_current_version() -> Optional[dict]:
    return read_version_record()


def register_model(record: dict, firestore_id: str = "current") -> None:
    """Write version record to Firestore model_versions and model_registry."""
    try:
        firestore_service.write_document("model_versions", record.get("model_version", firestore_id), record)
        firestore_service.write_document("model_registry", firestore_id, record)
    except Exception:
        pass
