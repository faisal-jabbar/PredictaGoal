"""Aggregated service status — used by /api/v1/system/status endpoint."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.monitoring.health_checks import full_health_report

_ROOT = Path(__file__).resolve().parents[2]
_STATUS_PATH = _ROOT / "data" / "reports" / "system_health_report.json"


def get_system_status() -> dict:
    report = full_health_report()

    api_ok       = report["api"].get("api_ok", False)
    firestore_ok = report["firestore"].get("firestore_ok", False)
    model_ok     = report["model"].get("exists", False)
    stale_count  = report["reports"].get("stale_count", 0)

    if api_ok and firestore_ok and model_ok and stale_count == 0:
        overall = "healthy"
    elif not api_ok or not model_ok:
        overall = "degraded"
    else:
        overall = "warning"

    status = {
        "overall": overall,
        "api_ok": api_ok,
        "firestore_ok": firestore_ok,
        "model_ok": model_ok,
        "stale_reports": stale_count,
        "details": report,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATUS_PATH.write_text(json.dumps(status, indent=2, default=str))

    return status
