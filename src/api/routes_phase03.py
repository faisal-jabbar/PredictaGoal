"""Phase 03 FastAPI routes — agent, system status, providers, retraining, audit, alerts, custom prediction."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.robustness.input_validator import CustomPredictionRequest, AgentQueryRequest
from src.robustness.rate_limit import is_allowed
from src.robustness.reliability_checks import check_model_ready
from src.monitoring import prometheus_metrics

_ROOT = Path(__file__).resolve().parents[2]
router = APIRouter()


# ── Pydantic models ────────────────────────────────────────────────────────────

class RetrainingTriggerRequest(BaseModel):
    force: bool = False
    reason: str = ""

class PreferencesRequest(BaseModel):
    favorite_teams: Optional[List[str]] = None
    min_confidence_alert: Optional[float] = None
    alert_on_high_drift: Optional[bool] = None
    alert_on_model_retrain: Optional[bool] = None
    channels: Optional[Dict[str, Any]] = None


# ── Helper ─────────────────────────────────────────────────────────────────────

def _load_json(rel: str) -> Optional[dict]:
    p = _ROOT / rel
    return json.loads(p.read_text()) if p.exists() else None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0] if forwarded else (request.client.host if request.client else "unknown")


# ── System status ──────────────────────────────────────────────────────────────

@router.get("/system/status")
def system_status():
    from src.monitoring.service_status import get_system_status
    return get_system_status()


# ── Provider status ────────────────────────────────────────────────────────────

@router.get("/providers/status")
def providers_status():
    from src.providers.provider_status import get_all_statuses
    return get_all_statuses()


# ── Agent ──────────────────────────────────────────────────────────────────────

@router.get("/agent/capabilities")
def agent_capabilities():
    from src.agent.query_agent import CAPABILITIES, _LLM_ENABLED
    return {
        "capabilities": CAPABILITIES,
        "llm_enabled": _LLM_ENABLED,
        "mode": "llm" if _LLM_ENABLED else "rule_based",
        "description": (
            "Rule-based deterministic agent over local report files. "
            "LLM mode available when OPENAI_API_KEY + ENABLE_LLM_AGENT=true."
        ),
    }


@router.post("/agent/query")
def agent_query(request: Request, body: AgentQueryRequest):
    ip = _client_ip(request)
    allowed, remaining = is_allowed(f"agent:{ip}", limit=30, window=60)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")

    from src.agent.query_agent import answer
    try:
        prometheus_metrics.prediction_requests_total.labels(endpoint="agent_query").inc()
        return answer(body.query, session_id=body.session_id)
    except Exception as e:
        prometheus_metrics.prediction_failures_total.labels(reason="agent_error").inc()
        raise HTTPException(status_code=500, detail="Agent error. See server logs.")


# ── Custom prediction ──────────────────────────────────────────────────────────

@router.post("/predictions/custom")
def custom_prediction(request: Request, body: CustomPredictionRequest):
    ip = _client_ip(request)
    allowed, _ = is_allowed(f"pred:{ip}", limit=20, window=60)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    readiness = check_model_ready()
    if not readiness["ready"]:
        raise HTTPException(status_code=503, detail=readiness["error"])

    start = time.time()
    try:
        from src.prediction.predict import predict_match
        import pandas as pd
        from src.config import settings
        processed_path = _ROOT / "data" / "processed" / "matches_processed.csv"
        if not processed_path.exists():
            raise HTTPException(status_code=503, detail="Processed dataset not found. Run preprocessing pipeline.")
        historical_df = pd.read_csv(str(processed_path))
        result = predict_match(
            home_team=body.home_team,
            away_team=body.away_team,
            match_date=body.match_date,
            historical_df=historical_df,
            tournament=body.tournament or "Friendly",
            neutral=body.neutral_venue or False,
        )

        # Confidence
        from src.confidence.confidence_calibration import calculate_pcs
        probs_list = [result["probabilities"].get(k, 0) for k in ["home_win", "draw", "away_win"]]
        pcs_report = calculate_pcs(probs_list)
        result["pcs"] = pcs_report.get("pcs")
        result["confidence_tier"] = pcs_report.get("confidence_tier")

        # Explanation
        try:
            from src.explanation.shap_explainer import get_rf_importances
            from src.explanation.rule_explainer import generate_explanation_text
            import joblib, json as _json
            model = joblib.load(str(_ROOT / "models" / "artifacts" / "football_match_model.joblib"))
            feat_path = _ROOT / "models" / "artifacts" / "feature_columns.json"
            feat_cols = _json.loads(feat_path.read_text()) if feat_path.exists() else []
            top_feats = get_rf_importances(model, feat_cols)[:5]
            explanation_text = generate_explanation_text(
                result["prediction"], result["probabilities"],
                top_feats, body.home_team, body.away_team,
            )
            result["explanation"] = explanation_text
            result["top_features"] = top_feats
        except Exception:
            result["explanation"] = "Explanation unavailable."
            result["top_features"] = []

        # Audit
        from src.audit import audit_service
        audit_id = audit_service.log("custom_prediction", {
            "home_team": body.home_team,
            "away_team": body.away_team,
            "match_date": body.match_date,
            "prediction": result.get("prediction"),
            "pcs": result.get("pcs"),
        })
        result["audit_event_id"] = audit_id

        # Metrics
        latency = time.time() - start
        prometheus_metrics.prediction_requests_total.labels(endpoint="custom_prediction").inc()
        prometheus_metrics.prediction_latency_seconds.observe(latency)

        return result

    except HTTPException:
        raise
    except Exception as e:
        prometheus_metrics.prediction_failures_total.labels(reason="custom_prediction_error").inc()
        raise HTTPException(status_code=500, detail="Prediction failed. Ensure model artifacts exist.")


# ── Retraining ─────────────────────────────────────────────────────────────────

@router.get("/retraining/status")
def retraining_status():
    d = _load_json("data/reports/retraining_decision.json")
    if not d:
        from src.orchestration.retraining_decision import evaluate_retraining_need
        d = evaluate_retraining_need()
    return d


@router.post("/retraining/trigger")
def retraining_trigger(body: RetrainingTriggerRequest):
    if not body.force:
        raise HTTPException(
            status_code=400,
            detail="Set force=true to confirm intentional retraining trigger.",
        )
    from src.orchestration.retraining_decision import evaluate_retraining_need
    from src.audit import audit_service
    decision = evaluate_retraining_need(force=True)
    audit_service.log("retraining_triggered", {"force": True, "reason": body.reason, "decision": decision})
    prometheus_metrics.retraining_decisions_total.labels(decision="manual_trigger").inc()
    return {"triggered": True, "decision": decision}


# ── Model version ──────────────────────────────────────────────────────────────

@router.get("/model/version")
def model_version():
    d = _load_json("data/reports/model_registry_report.json")
    if not d:
        raise HTTPException(status_code=404, detail="No model version record found. Run training pipeline.")
    return d


# ── Audit trail ────────────────────────────────────────────────────────────────

@router.get("/audit/recent")
def audit_recent(n: int = 20):
    from src.audit import audit_service
    events = audit_service.recent_events(n)
    integrity = audit_service.chain_integrity()
    return {"events": events, "integrity": integrity}


# ── Alerts ────────────────────────────────────────────────────────────────────

@router.get("/alerts/recent")
def alerts_recent(n: int = 10):
    from src.alerts.alert_service import get_recent_alerts
    return {"alerts": get_recent_alerts(n)}


# ── Preferences ───────────────────────────────────────────────────────────────

@router.post("/preferences")
def save_prefs(body: PreferencesRequest, user_id: str = "default_user"):
    from src.alerts.user_preferences import get_preferences, save_preferences
    current = get_preferences(user_id)
    if body.favorite_teams is not None:
        current["favorite_teams"] = body.favorite_teams
    if body.min_confidence_alert is not None:
        current["min_confidence_alert"] = body.min_confidence_alert
    if body.alert_on_high_drift is not None:
        current["alert_on_high_drift"] = body.alert_on_high_drift
    if body.alert_on_model_retrain is not None:
        current["alert_on_model_retrain"] = body.alert_on_model_retrain
    if body.channels is not None:
        current["channels"] = body.channels
    saved = save_preferences(user_id, current)
    return saved


@router.get("/preferences/{user_id}")
def get_prefs(user_id: str):
    from src.alerts.user_preferences import get_preferences
    return get_preferences(user_id)
