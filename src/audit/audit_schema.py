"""Audit event schema — defines the structure of every audit record."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


VALID_EVENT_TYPES = {
    "dataset_download",
    "preprocessing",
    "feature_generation",
    "model_training",
    "model_retraining_decision",
    "model_promotion",
    "prediction_generated",
    "explanation_generated",
    "confidence_calculated",
    "drift_detected",
    "alert_generated",
    "api_health_check",
    "agent_query",
    "dashboard_report_read",
    "provider_check",
    "system_startup",
    "custom_prediction",
    "retraining_triggered",
}


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    event_type: str
    actor: str
    phase: str
    details: Dict[str, Any]
    hash: str
    previous_hash: str
    session_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "phase": self.phase,
            "details": self.details,
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "session_id": self.session_id,
        }
