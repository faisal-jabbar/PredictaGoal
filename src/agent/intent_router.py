"""Intent classification — maps a natural language query to a known intent."""

import re
from typing import Tuple

INTENTS = {
    "latest_prediction":     ["predict", "prediction", "who will win", "match result", "outcome"],
    "explain_prediction":    ["why", "explain", "reason", "because", "how did", "what drove", "shap"],
    "model_accuracy":        ["accuracy", "how accurate", "performance", "correct", "score", "precision"],
    "model_limitations":     ["limitation", "weakness", "drawback", "can't", "unable", "fail"],
    "drift_status":          ["drift", "psi", "distribution shift", "data drift", "feature drift"],
    "bias_fairness":         ["bias", "fair", "fairness", "imbalance", "draw accuracy", "class accuracy"],
    "dataset_summary":       ["dataset", "data", "how many matches", "training data", "rows", "history"],
    "confidence_explanation":["confidence", "pcs", "low confidence", "uncertain", "reliable", "entropy"],
    "context_availability":  ["context", "weather", "injury", "referee", "available context", "external"],
    "how_to_run":            ["how to run", "start", "setup", "install", "command", "run the system"],
    "retraining_status":     ["retrain", "retraining", "model update", "new model", "drift triggered"],
    "provider_status":       ["provider", "api", "football api", "kaggle", "fixture", "weather api"],
    "audit_trail":           ["audit", "log", "history", "trail", "immutable", "event"],
    "system_health":         ["health", "status", "system", "backend", "online", "operational"],
}

_NOT_AVAILABLE = "not_available"


def classify(query: str) -> Tuple[str, float]:
    """Return (intent, confidence 0–1). Falls back to not_available."""
    q = query.lower()
    best_intent = _NOT_AVAILABLE
    best_score  = 0

    for intent, keywords in INTENTS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score > best_score:
            best_score = score
            best_intent = intent

    confidence = min(1.0, best_score / 3.0) if best_score > 0 else 0.0
    return best_intent, confidence
