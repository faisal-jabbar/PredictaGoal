"""Prometheus metrics definitions — single source of truth for all counters/gauges.

Import this module to get references to metrics objects.
The FastAPI /metrics endpoint calls generate_latest() to serve them.
"""

from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, REGISTRY

# ── Prediction metrics ────────────────────────────────────────
prediction_requests_total = Counter(
    "predictagoal_prediction_requests_total",
    "Total prediction requests received",
    ["endpoint"],
    registry=REGISTRY,
)

prediction_failures_total = Counter(
    "predictagoal_prediction_failures_total",
    "Total prediction requests that failed",
    ["reason"],
    registry=REGISTRY,
)

prediction_latency_seconds = Histogram(
    "predictagoal_prediction_latency_seconds",
    "Prediction request latency in seconds",
    registry=REGISTRY,
)

# ── Agent metrics ─────────────────────────────────────────────
agent_queries_total = Counter(
    "predictagoal_agent_queries_total",
    "Total agent query requests",
    ["intent"],
    registry=REGISTRY,
)

# ── Model metrics ─────────────────────────────────────────────
model_accuracy_gauge = Gauge(
    "predictagoal_model_accuracy",
    "Current model accuracy on test set",
    registry=REGISTRY,
)

drift_level_gauge = Gauge(
    "predictagoal_drift_level",
    "Current drift level (0=none,1=low,2=medium,3=high)",
    registry=REGISTRY,
)

# ── Infrastructure metrics ────────────────────────────────────
firestore_up = Gauge(
    "predictagoal_firestore_up",
    "Firestore availability (1=up, 0=down)",
    registry=REGISTRY,
)

stale_reports_count = Gauge(
    "predictagoal_stale_reports_count",
    "Number of reports older than 24h",
    registry=REGISTRY,
)

# ── MLOps metrics ─────────────────────────────────────────────
retraining_decisions_total = Counter(
    "predictagoal_retraining_decisions_total",
    "Total retraining decisions made",
    ["decision"],
    registry=REGISTRY,
)

model_promotions_total = Counter(
    "predictagoal_model_promotions_total",
    "Total model promotions (champion replaced)",
    registry=REGISTRY,
)

# ── Alert metrics ─────────────────────────────────────────────
alert_events_total = Counter(
    "predictagoal_alert_events_total",
    "Total alert events generated",
    ["alert_type"],
    registry=REGISTRY,
)

# ── Pipeline metrics ──────────────────────────────────────────
pipeline_runs_total = Counter(
    "predictagoal_pipeline_runs_total",
    "Total pipeline DAG runs",
    ["pipeline", "status"],
    registry=REGISTRY,
)


def initialise_gauges_from_reports():
    """Read local report files and seed gauge values at startup."""
    import json
    import logging
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]

    # Model accuracy — key is "accuracy" in model_training_report.json
    model_report = root / "models" / "reports" / "model_training_report.json"
    if model_report.exists():
        try:
            d = json.loads(model_report.read_text())
            # Support both "accuracy" (Phase 01 key) and legacy "test_accuracy"
            acc = d.get("accuracy") or d.get("test_accuracy")
            if acc is not None and acc > 0:
                model_accuracy_gauge.set(float(acc))
            else:
                logging.warning(
                    "predictagoal_model_accuracy: accuracy key missing or zero "
                    "in model_training_report.json — gauge not updated"
                )
        except Exception as exc:
            logging.warning("initialise_gauges_from_reports: model accuracy read failed: %s", exc)

    # Drift level
    drift_map = {"none": 0, "low": 1, "medium": 2, "high": 3}
    drift_report = root / "data" / "reports" / "drift_report.json"
    if drift_report.exists():
        try:
            d = json.loads(drift_report.read_text())
            level = d.get("overall_drift_level", "none")
            drift_level_gauge.set(drift_map.get(level, 0))
        except Exception as exc:
            logging.warning("initialise_gauges_from_reports: drift level read failed: %s", exc)

    # Firestore availability — live check at startup
    try:
        from src.database.firebase_client import is_firebase_available
        firestore_up.set(1.0 if is_firebase_available() else 0.0)
    except Exception as exc:
        logging.warning("initialise_gauges_from_reports: Firestore check failed: %s", exc)
        firestore_up.set(0.0)
