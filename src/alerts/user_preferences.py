"""User preference storage — local JSON with Firestore sync."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parents[2]
_PREFS_DIR = _ROOT / "data" / "preferences"

_DEFAULT_PREFS = {
    "favorite_teams": ["Brazil", "Argentina"],
    "min_confidence_alert": 0.6,
    "alert_on_high_drift": True,
    "alert_on_model_retrain": True,
    "alert_on_model_promotion": True,
    "channels": {"email": False},
}


def _prefs_path(user_id: str) -> Path:
    _PREFS_DIR.mkdir(parents=True, exist_ok=True)
    return _PREFS_DIR / f"{user_id}.json"


def get_preferences(user_id: str = "default_user") -> Dict[str, Any]:
    p = _prefs_path(user_id)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    prefs = {"user_id": user_id, **_DEFAULT_PREFS, "created_at": datetime.now(timezone.utc).isoformat()}
    save_preferences(user_id, prefs)
    return prefs


def save_preferences(user_id: str, prefs: Dict[str, Any]) -> Dict[str, Any]:
    prefs["user_id"] = user_id
    prefs["updated_at"] = datetime.now(timezone.utc).isoformat()
    p = _prefs_path(user_id)
    p.write_text(json.dumps(prefs, indent=2))

    try:
        from src.database import firestore_service
        firestore_service.write_document("user_preferences", user_id, prefs)
    except Exception:
        pass

    return prefs
