"""Alert rule evaluation — checks conditions and returns triggered alerts."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[2]


def _load_json(rel: str) -> dict:
    p = _ROOT / rel
    return json.loads(p.read_text()) if p.exists() else {}


def evaluate_rules(user_prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluate all alert rules against current reports. Returns list of triggered alerts."""
    alerts = []
    now = datetime.now(timezone.utc).isoformat()

    # High drift alert
    if user_prefs.get("alert_on_high_drift", True):
        drift = _load_json("data/reports/drift_report.json")
        if drift.get("overall_drift_level") == "high":
            alerts.append({
                "alert_type": "high_drift",
                "severity": "warning",
                "message": f"High feature drift detected. Max PSI={drift.get('max_psi', 0):.4f}. "
                           f"Drifted features: {', '.join(drift.get('drifted_features', []))}.",
                "timestamp": now,
            })

    # Model retrain alert (check if retraining_decision says retrain_needed)
    if user_prefs.get("alert_on_model_retrain", True):
        decision = _load_json("data/reports/retraining_decision.json")
        if decision.get("status") == "retrain_needed":
            alerts.append({
                "alert_type": "model_retrain_needed",
                "severity": "info",
                "message": f"Retraining recommended. Reasons: {'; '.join(decision.get('reasons', []))}.",
                "timestamp": now,
            })

    # Model promotion alert
    if user_prefs.get("alert_on_model_promotion", True):
        version = _load_json("data/reports/model_registry_report.json")
        if version.get("promoted"):
            alerts.append({
                "alert_type": "model_promoted",
                "severity": "info",
                "message": f"Model promoted to version {version.get('model_version')}. "
                           f"Accuracy: {version.get('accuracy', 0):.4f}.",
                "timestamp": now,
            })

    # Favorite team prediction
    fav_teams = set(t.lower() for t in user_prefs.get("favorite_teams", []))
    pred = _load_json("data/reports/sample_prediction.json")
    home = (pred.get("home_team") or "").lower()
    away = (pred.get("away_team") or "").lower()
    if fav_teams and (home in fav_teams or away in fav_teams):
        pcs = pred.get("pcs", 0)
        min_conf = user_prefs.get("min_confidence_alert", 0.6)
        if pcs >= min_conf:
            alerts.append({
                "alert_type": "favorite_team_prediction",
                "severity": "info",
                "message": f"Prediction available for a followed team: "
                           f"{pred.get('home_team')} vs {pred.get('away_team')}. "
                           f"PCS={pcs:.3f}.",
                "timestamp": now,
            })

    return alerts
