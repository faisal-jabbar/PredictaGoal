"""
Firestore CRUD helpers. Every write falls back to local_storage when Firebase is unavailable.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from src.database.firebase_client import get_firestore_client, is_firebase_available
from src.database import local_storage
from src.utils.logger import get_logger

log = get_logger(__name__)


def _collection(name: str):
    db = get_firestore_client()
    if db is None:
        raise RuntimeError("Firestore not available")
    return db.collection(name)


def write_document(
    collection: str,
    doc_id: str,
    data: Dict[str, Any],
    fallback_path: Optional[str] = None,
) -> bool:
    data["_written_at"] = datetime.utcnow().isoformat()

    if is_firebase_available():
        try:
            _collection(collection).document(doc_id).set(data)
            log.info(f"Firestore write OK: {collection}/{doc_id}")
            return True
        except Exception as exc:
            log.error(f"Firestore write failed ({collection}/{doc_id}): {exc}")

    if fallback_path:
        local_storage.save_local(data, fallback_path)
        log.info(f"Local fallback saved: {fallback_path}")
    return False


def read_document(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    if not is_firebase_available():
        log.warning("Firestore unavailable — cannot read document.")
        return None
    try:
        doc = _collection(collection).document(doc_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as exc:
        log.error(f"Firestore read failed ({collection}/{doc_id}): {exc}")
        return None


def log_pipeline_event(event: str, details: Dict[str, Any]) -> None:
    from src.config.settings import COLLECTION_LOGS
    import time

    doc_id = f"{event}_{int(time.time())}"
    payload = {"event": event, "details": details, "timestamp": datetime.utcnow().isoformat()}
    write_document(COLLECTION_LOGS, doc_id, payload)
