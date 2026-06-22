# PredictaGoal — System Architecture

## Layered Architecture

```
PRESENTATION
  React 18 + Vite + TailwindCSS + Recharts
  Panels: KPI, Prediction, Confidence, Explanation, Drift, Bias, Context,
          Agent Query, Custom Prediction, Audit, Alerts, Provider Status

API GATEWAY
  FastAPI 0.110+ / Uvicorn
  CORS enabled | Rate limiting (in-memory sliding window)
  Input validation (Pydantic v2 + custom sanitisation)
  Prometheus /metrics endpoint

AGENT CORE
  query_agent.py       — intent classify + response build
  intent_router.py     — keyword-based intent classification (14 intents)
  response_builder.py  — reads local reports, builds factual answers
  tools.py             — reads JSON report files (no hallucination)

ORCHESTRATION
  Airflow DAGs         — daily pipeline, retraining, monitoring
  retraining_decision  — PSI >= 0.25 or HIGH drift triggers retrain
  model_promotion      — Champion/Challenger gate before promoting

ML ENGINE
  Feature Engineering  — 14 leak-free features (Elo, form, H2H, goals, venue)
  RandomForest         — 200 trees, balanced weights, seed=42
  Confidence (PCS)     — margin-score formula (not entropy-based)
  SHAP / RF importance — top feature explanation
  MLflow               — experiment tracking + model versioning

MONITORING
  Prometheus           — 14 custom metrics (counters, gauges, histograms)
  Grafana              — auto-provisioned dashboard (11 panels)
  Health checks        — API, Firestore, reports, model artifact

DATA LAYER
  Firestore (primary)  — 20+ collections
  Local JSON (fallback)— data/reports/, models/reports/
  Audit log            — data/audit/audit_log.jsonl (SHA-256 hash chain)
  MLflow runs          — mlruns/ (file-based by default)

PROVIDERS
  KaggleProvider       — real KaggleHub dataset pipeline
  WeatherProvider      — Open-Meteo (free, no key required, needs lat/lon)
  FixturesProvider     — football-data.org / API-Football (requires key)
  InjuryProvider       — custom feed (requires key)

ALERTS
  AlertRules           — evaluates drift, retrain, promotion, favorite team
  AlertService         — writes to Firestore alerts + alert_events
  EmailNotifier        — SMTP (disabled unless configured)
  UserPreferences      — local JSON + Firestore user_preferences

INFRA
  Docker Compose       — backend, frontend, mlflow, airflow, prometheus, grafana
  Postgres             — Airflow metadata store
```

## Firestore Collections

Phase 01: dataset_summaries, data_quality_reports, model_runs, sample_predictions, pipeline_logs
Phase 02: confidence_reports, explanations, drift_reports, bias_reports, contextual_reports
Phase 03: audit_events, alerts, alert_events, user_preferences, model_versions, model_registry,
          retraining_decisions, provider_status, agent_queries, system_health
