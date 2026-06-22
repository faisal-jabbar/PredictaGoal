"""Alert service — evaluates rules, stores locally and in Firestore, optionally emails."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.alerts.alert_rules import evaluate_rules
from src.alerts.user_preferences import get_preferences
from src.alerts.email_notifier import send_alert_email
from src.audit import audit_service
from src.database import firestore_service
from src.monitoring import prometheus_metrics

_ROOT = Path(__file__).resolve().parents[2]
_ALERTS_PATH = _ROOT / "data" / "reports" / "alerts_report.json"


def run_alert_cycle(user_id: str = "default_user") -> Dict[str, Any]:
    """Full alert evaluation cycle. Returns report."""
    prefs = get_preferences(user_id)
    triggered = evaluate_rules(prefs)

    results = []
    for alert in triggered:
        alert_id = str(uuid.uuid4())
        alert["alert_id"] = alert_id
        alert["user_id"] = user_id

        # Firestore
        try:
            firestore_service.write_document("alerts", alert_id, alert)
            firestore_service.write_document("alert_events", alert_id, {**alert, "stored_at": datetime.now(timezone.utc).isoformat()})
        except Exception:
            pass

        # Prometheus
        try:
            prometheus_metrics.alert_events_total.labels(alert_type=alert.get("alert_type", "unknown")).inc()
        except Exception:
            pass

        # Audit
        audit_service.log("alert_generated", {"alert_type": alert.get("alert_type"), "alert_id": alert_id})

        # Email (only if configured)
        email_result = send_alert_email(
            subject=alert.get("alert_type", "Alert"),
            body=alert.get("message", ""),
        )
        alert["email_result"] = email_result
        results.append(alert)

    report = {
        "user_id": user_id,
        "alerts_triggered": len(results),
        "alerts": results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _ALERTS_PATH.write_text(json.dumps(report, indent=2, default=str))

    return report


def get_recent_alerts(n: int = 10) -> List[Dict[str, Any]]:
    if _ALERTS_PATH.exists():
        try:
            data = json.loads(_ALERTS_PATH.read_text())
            return data.get("alerts", [])[-n:]
        except Exception:
            pass
    return []
