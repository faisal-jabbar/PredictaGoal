"""Health checks for backend, Firestore, reports, and model artifact."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

import urllib.request

_ROOT = Path(__file__).resolve().parents[2]

REPORT_FILES = [
    "data/reports/confidence_report.json",
    "data/reports/explanation_report.json",
    "data/reports/drift_report.json",
    "data/reports/bias_report.json",
    "data/reports/contextual_report.json",
]
MODEL_ARTIFACT = "models/artifacts/football_match_model.joblib"
STALE_HOURS = 24


def check_api_health(url: str = "http://localhost:8000/health") -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
        return {"api_ok": True, **data}
    except Exception as e:
        return {"api_ok": False, "error": str(e)}


def check_report_freshness() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=STALE_HOURS)
    stale, fresh, missing = [], [], []
    for rel in REPORT_FILES:
        p = _ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            stale.append(rel)
        else:
            fresh.append(rel)
    return {
        "fresh": fresh,
        "stale": stale,
        "missing": missing,
        "stale_count": len(stale) + len(missing),
        "checked_at": now.isoformat(),
    }


def check_model_artifact() -> Dict[str, Any]:
    p = _ROOT / MODEL_ARTIFACT
    return {
        "exists": p.exists(),
        "path": str(p),
        "size_bytes": p.stat().st_size if p.exists() else 0,
    }


def check_firestore() -> Dict[str, Any]:
    try:
        from src.database.firebase_client import get_firestore_client
        db = get_firestore_client()
        if db is None:
            return {"firestore_ok": False, "reason": "client_none"}
        list(db.collection("system_health").limit(1).stream())
        return {"firestore_ok": True}
    except Exception as e:
        return {"firestore_ok": False, "reason": str(e)}


def full_health_report() -> Dict[str, Any]:
    return {
        "api":      check_api_health(),
        "reports":  check_report_freshness(),
        "model":    check_model_artifact(),
        "firestore": check_firestore(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
