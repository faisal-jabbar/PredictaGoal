"""Query agent — main entry point for FR10 conversational interface.

Deterministic rule-based by default.
Optional LLM mode activated when OPENAI_API_KEY + ENABLE_LLM_AGENT=true.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.agent.intent_router import classify
from src.agent.response_builder import build
from src.audit import audit_service
from src.monitoring import prometheus_metrics

_ROOT = Path(__file__).resolve().parents[2]
_QUERY_REPORT = _ROOT / "data" / "reports" / "agent_query_report.json"

CAPABILITIES = [
    "latest_prediction",
    "explain_prediction",
    "model_accuracy",
    "model_limitations",
    "drift_status",
    "bias_fairness",
    "dataset_summary",
    "confidence_explanation",
    "context_availability",
    "how_to_run",
    "retraining_status",
    "provider_status",
    "audit_trail",
    "system_health",
]

_LLM_ENABLED = (
    os.getenv("ENABLE_LLM_AGENT", "false").lower() == "true"
    and bool(os.getenv("OPENAI_API_KEY"))
)


def _llm_answer(query: str, base_answer: str) -> Optional[str]:
    """Optionally enrich the rule-based answer with LLM narrative."""
    if not _LLM_ENABLED:
        return None
    try:
        import openai
        client = openai.OpenAI()
        system_prompt = (
            "You are PredictaGoal, an AI football analytics assistant. "
            "Answer strictly based on the provided data. "
            "Do not invent statistics. Do not give betting advice. "
            "Be concise and professional."
        )
        user_msg = f"Context data answer: {base_answer}\n\nUser question: {query}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user",   "content": user_msg}],
            max_tokens=300,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def answer(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a user query and return a structured response."""
    session_id = session_id or str(uuid.uuid4())
    intent, conf = classify(query)

    response = build(intent, conf)

    # Optional LLM enrichment
    if _LLM_ENABLED and response.get("status") == "ok":
        llm_text = _llm_answer(query, response.get("answer", ""))
        if llm_text:
            response["answer"] = llm_text
            response["llm_enhanced"] = True

    response["query"] = query
    response["session_id"] = session_id
    response["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Metrics
    try:
        prometheus_metrics.agent_queries_total.labels(intent=intent).inc()
    except Exception:
        pass

    # Audit
    audit_service.log(
        "agent_query",
        {"query_length": len(query), "intent": intent, "intent_confidence": conf},
        session_id=session_id,
    )

    # Persist last query report
    _QUERY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    _QUERY_REPORT.write_text(json.dumps(response, indent=2, default=str))

    # Firestore
    try:
        from src.database import firestore_service
        firestore_service.write_document("agent_queries", session_id, response)
    except Exception:
        pass

    return response
