"""Immutable, hash-chained audit logger.

Each event includes:
  hash = sha256(previous_hash + timestamp + event_type + json(details))

The log file is append-only JSONL at data/audit/audit_log.jsonl.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.audit.audit_schema import AuditEvent

LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "audit" / "audit_log.jsonl"


def _sha256(previous_hash: str, timestamp: str, event_type: str, details: dict) -> str:
    payload = previous_hash + timestamp + event_type + json.dumps(details, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _get_last_hash() -> str:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
        return "0" * 64
    with open(LOG_PATH, "rb") as f:
        # Read last non-empty line efficiently
        f.seek(0, 2)
        size = f.tell()
        pos = max(0, size - 4096)
        f.seek(pos)
        lines = f.read().decode("utf-8", errors="replace").strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line:
            try:
                return json.loads(line).get("hash", "0" * 64)
            except Exception:
                pass
    return "0" * 64


def append_event(
    event_type: str,
    details: Dict[str, Any],
    actor: str = "system",
    phase: str = "Phase 03",
    session_id: Optional[str] = None,
) -> AuditEvent:
    """Write one immutable audit event. Returns the AuditEvent."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    event_id = str(uuid.uuid4())
    prev_hash = _get_last_hash()
    h = _sha256(prev_hash, now, event_type, details)

    event = AuditEvent(
        event_id=event_id,
        timestamp=now,
        event_type=event_type,
        actor=actor,
        phase=phase,
        details=details,
        hash=h,
        previous_hash=prev_hash,
        session_id=session_id,
    )

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event.to_dict(), default=str) + "\n")

    return event


def read_recent(n: int = 20) -> list:
    """Return the n most recent audit events."""
    if not LOG_PATH.exists():
        return []
    events = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    return events[-n:]


def verify_chain(max_events: int = 1000) -> Dict[str, Any]:
    """Verify hash chain integrity. Returns a report dict."""
    if not LOG_PATH.exists():
        return {"valid": True, "events_checked": 0, "note": "No log file yet."}

    events = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    events = events[:max_events]

    broken_at = None
    for i, ev in enumerate(events):
        prev = events[i - 1]["hash"] if i > 0 else "0" * 64
        expected = _sha256(prev, ev["timestamp"], ev["event_type"], ev["details"])
        if expected != ev["hash"]:
            broken_at = i
            break

    return {
        "valid": broken_at is None,
        "events_checked": len(events),
        "broken_at_index": broken_at,
    }
