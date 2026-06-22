"""Response builder — turns intent + report data into a structured answer."""

from typing import Any, Dict, List

from src.agent import tools


_NOT_AVAILABLE_RESPONSE = {
    "answer": "This information is not available in the current dataset or reports.",
    "status": "not_available",
    "sources": [],
}


def build(intent: str, intent_confidence: float) -> Dict[str, Any]:
    builders = {
        "latest_prediction":     _prediction,
        "explain_prediction":    _explanation,
        "model_accuracy":        _accuracy,
        "model_limitations":     _limitations,
        "drift_status":          _drift,
        "bias_fairness":         _bias,
        "dataset_summary":       _dataset,
        "confidence_explanation":_confidence,
        "context_availability":  _context,
        "how_to_run":            _how_to_run,
        "retraining_status":     _retraining,
        "provider_status":       _providers,
        "audit_trail":           _audit,
        "system_health":         _health,
        "not_available":         lambda: _NOT_AVAILABLE_RESPONSE,
    }
    fn = builders.get(intent, lambda: _NOT_AVAILABLE_RESPONSE)
    result = fn()
    result["intent"] = intent
    result["intent_confidence"] = round(intent_confidence, 2)
    return result


def _prediction() -> Dict[str, Any]:
    d = tools.get_prediction()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/08_run_prediction.py"}
    pred = d.get("prediction", "unknown").replace("_", " ").title()
    home = d.get("home_team", "?")
    away = d.get("away_team", "?")
    probs = d.get("probabilities", {})
    return {
        "answer": (
            f"The latest sample prediction is {pred} for {home} vs {away} "
            f"(date: {d.get('match_date', '?')}, tournament: {d.get('tournament', '?')}). "
            f"Probabilities — Home Win: {probs.get('home_win',0):.1%}, "
            f"Draw: {probs.get('draw',0):.1%}, "
            f"Away Win: {probs.get('away_win',0):.1%}."
        ),
        "sources": ["sample_prediction.json"],
        "status": "ok",
        "data": d,
    }


def _explanation() -> Dict[str, Any]:
    d = tools.get_explanation()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/09_generate_explanations.py"}
    top = d.get("top_features", [])[:3]
    top_str = ", ".join(f"{f.get('display_name', f.get('feature'))} ({f.get('importance',0):.1%})" for f in top)
    return {
        "answer": (
            f"{d.get('explanation_text', 'Explanation not available.')} "
            f"Top driving features: {top_str}."
        ),
        "sources": ["explanation_report.json", "confidence_report.json"],
        "status": "ok",
        "data": {"top_features": top, "method": d.get("method")},
    }


def _accuracy() -> Dict[str, Any]:
    d = tools.get_model_report()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/07_train_model.py"}
    acc = d.get("test_accuracy", 0)
    return {
        "answer": (
            f"The current model achieves {acc:.1%} accuracy on the held-out test set "
            f"({d.get('test_size', '?')} matches). This is a {d.get('model_type', 'RandomForest')} model "
            f"with {d.get('n_features', 14)} engineered features. "
            f"Note: football outcomes have irreducible uncertainty — 55–70% is a realistic ceiling."
        ),
        "sources": ["model_training_report.json"],
        "status": "ok",
    }


def _limitations() -> Dict[str, Any]:
    return {
        "answer": (
            "Known limitations: (1) The model is trained on historical results only — "
            "it lacks real-time injury, weather, or referee data. "
            "(2) Draw prediction is the weakest class (~30% recall) due to class imbalance. "
            "(3) Feature drift is currently HIGH for Elo features, which may affect reliability. "
            "(4) External data providers (fixtures, weather, injuries) require API keys not currently configured. "
            "(5) Football outcomes have irreducible randomness — no model can exceed ~70% accuracy."
        ),
        "sources": ["bias_report.json", "drift_report.json"],
        "status": "ok",
    }


def _drift() -> Dict[str, Any]:
    d = tools.get_drift()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/11_generate_drift_report.py"}
    level = d.get("overall_drift_level", "?")
    return {
        "answer": (
            f"Current drift level: {level.upper()}. "
            f"Max PSI: {d.get('max_psi', 0):.4f}. "
            f"Drifted features: {', '.join(d.get('drifted_features', [])) or 'none'}. "
            f"{d.get('notes', '')}"
        ),
        "sources": ["drift_report.json"],
        "status": "ok",
        "data": {"level": level, "max_psi": d.get("max_psi")},
    }


def _bias() -> Dict[str, Any]:
    d = tools.get_bias()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/12_generate_bias_report.py"}
    acc_cls = d.get("accuracy_by_class", {})
    acc_str = ", ".join(f"{k.replace('_',' ').title()}: {v:.1%}" for k, v in acc_cls.items())
    return {
        "answer": (
            f"Overall model accuracy: {d.get('overall_accuracy', 0):.1%}. "
            f"By outcome class — {acc_str}. "
            f"{d.get('known_issue', '')} {d.get('fairness_notes', '')}"
        ),
        "sources": ["bias_report.json"],
        "status": "ok",
    }


def _dataset() -> Dict[str, Any]:
    d = tools.get_model_report()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/07_train_model.py"}
    return {
        "answer": (
            f"The dataset contains {d.get('train_size', 0) + d.get('test_size', 0):,} cleaned matches "
            f"(after {d.get('dropped_invalid', 0)} invalid rows removed). "
            f"Training: {d.get('train_size', 0):,} matches | Test: {d.get('test_size', 0):,} matches. "
            f"Date range: {d.get('date_range_from', '?')} to {d.get('date_range_to', '?')}. "
            f"Features: {d.get('n_features', 14)} engineered signals."
        ),
        "sources": ["model_training_report.json"],
        "status": "ok",
    }


def _confidence() -> Dict[str, Any]:
    d = tools.get_confidence()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run scripts/10_calculate_confidence.py"}
    return {
        "answer": (
            f"The Prediction Confidence Score (PCS) is {d.get('pcs', 0):.3f} "
            f"(tier: {d.get('confidence_tier', '?')}). "
            f"PCS measures how decisive the probability gap is — it is lower when all three outcomes "
            f"have similar probabilities. {d.get('confidence_note', '')}"
        ),
        "sources": ["confidence_report.json"],
        "status": "ok",
        "data": {"pcs": d.get("pcs"), "tier": d.get("confidence_tier")},
    }


def _context() -> Dict[str, Any]:
    d = tools.get_contextual()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE}
    avail = list(d.get("available_context", {}).keys())
    unavail = list(d.get("unavailable_context", {}).keys())
    return {
        "answer": (
            f"Context coverage: {d.get('context_coverage_pct', 0)}%. "
            f"Available from dataset: {', '.join(avail)}. "
            f"Not available (require external APIs): {', '.join(unavail)}. "
            f"{d.get('notes', '')}"
        ),
        "sources": ["contextual_report.json"],
        "status": "ok",
    }


def _how_to_run() -> Dict[str, Any]:
    return {
        "answer": (
            "To run PredictaGoal: "
            "(1) Start the backend: python -m uvicorn src.api.main:app --reload "
            "(2) Start the frontend: cd frontend && npm run dev "
            "(3) Open the dashboard: http://localhost:5173 "
            "(4) API docs: http://localhost:8000/docs "
            "(5) MLflow UI: mlflow ui --host 127.0.0.1 --port 5000 "
            "(6) Docker full-stack: docker compose up --build "
            "See README.md and docs/RUNBOOK.md for full instructions."
        ),
        "sources": ["README.md", "docs/RUNBOOK.md"],
        "status": "ok",
    }


def _retraining() -> Dict[str, Any]:
    d = tools.get_retraining_decision()
    v = tools.get_model_version()
    if not d:
        return {**_NOT_AVAILABLE_RESPONSE, "hint": "Run a retraining evaluation first."}
    return {
        "answer": (
            f"Retraining status: {'NEEDED' if d.get('should_retrain') else 'NOT NEEDED'}. "
            f"Reasons: {'; '.join(d.get('reasons', ['None']))}. "
            f"Current model version: {v.get('model_version', 'unknown') if v else 'unknown'}."
        ),
        "sources": ["retraining_decision.json", "model_registry_report.json"],
        "status": "ok",
        "data": {"should_retrain": d.get("should_retrain")},
    }


def _providers() -> Dict[str, Any]:
    try:
        from src.providers.provider_status import get_all_statuses
        report = get_all_statuses()
        providers = report.get("providers", {})
        summary = "; ".join(f"{k}: {v.get('status', '?')}" for k, v in providers.items())
        return {
            "answer": f"Provider status — {summary}.",
            "sources": ["provider_status_report.json"],
            "status": "ok",
            "data": providers,
        }
    except Exception as e:
        return {**_NOT_AVAILABLE_RESPONSE, "error": str(e)}


def _audit() -> Dict[str, Any]:
    try:
        from src.audit import audit_logger
        events = audit_logger.read_recent(5)
        if not events:
            return {**_NOT_AVAILABLE_RESPONSE, "hint": "Audit log is empty — run a pipeline script first."}
        summary = "; ".join(f"{e.get('event_type')} at {e.get('timestamp','')[:19]}" for e in events)
        integrity = audit_logger.verify_chain()
        return {
            "answer": (
                f"Audit trail contains recent events: {summary}. "
                f"Chain integrity: {'valid' if integrity.get('valid') else 'BROKEN — investigate immediately'}. "
                f"Total events checked: {integrity.get('events_checked', 0)}."
            ),
            "sources": ["data/audit/audit_log.jsonl"],
            "status": "ok",
        }
    except Exception as e:
        return {**_NOT_AVAILABLE_RESPONSE, "error": str(e)}


def _health() -> Dict[str, Any]:
    try:
        from src.monitoring.health_checks import check_api_health, check_model_artifact
        api = check_api_health()
        model = check_model_artifact()
        return {
            "answer": (
                f"System health — API: {'online' if api.get('api_ok') else 'offline'}. "
                f"Firebase: {api.get('firebase', 'unknown')}. "
                f"Model artifact: {'present' if model.get('exists') else 'missing'}."
            ),
            "sources": ["health_checks"],
            "status": "ok",
        }
    except Exception as e:
        return {**_NOT_AVAILABLE_RESPONSE, "error": str(e)}
