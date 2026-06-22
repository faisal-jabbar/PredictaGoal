"""High-level audit service — thin wrapper used by other modules."""

from typing import Any, Dict, Optional

from src.audit import audit_logger
from src.database import firestore_service


def log(
    event_type: str,
    details: Dict[str, Any],
    actor: str = "system",
    phase: str = "Phase 03",
    session_id: Optional[str] = None,
    write_firestore: bool = True,
) -> str:
    """Append audit event locally and optionally write to Firestore. Returns event_id."""
    event = audit_logger.append_event(event_type, details, actor, phase, session_id)

    if write_firestore:
        try:
            firestore_service.write_document("audit_events", event.event_id, event.to_dict())
        except Exception:
            pass  # local log is primary; Firestore is secondary

    return event.event_id


def recent_events(n: int = 20) -> list:
    return audit_logger.read_recent(n)


def chain_integrity() -> dict:
    return audit_logger.verify_chain()
