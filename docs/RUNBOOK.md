# PredictaGoal Runbook

## Starting Services (Local)

### FastAPI backend
```bash
python -m uvicorn src.api.main:app --reload --port 8000
```

### React frontend
```bash
cd frontend && npm run dev
```

### MLflow UI
```bash
mlflow ui --host 127.0.0.1 --port 5000
```

### Airflow (requires apache-airflow installed)
```bash
pip install apache-airflow
set AIRFLOW_HOME=%cd%\airflow          # Windows
export AIRFLOW_HOME=$(pwd)/airflow     # Linux/Mac
airflow db init
airflow standalone
# UI: http://localhost:8080
```

### Prometheus + Grafana (Docker)
```bash
docker compose up prometheus grafana
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/predictagoal)
```

---

## Pipeline Run Order

### Phase 01
```
01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08
env  fire  kag  down  pre  feat  train  pred
```

### Phase 02
```
09 -> 10 -> 11 -> 12 -> 13
exp  conf  drft  bias  verify
```

### Phase 03
```
14 -> 15 -> 16 -> 17 -> 18
air  mlfow monit agent  final
```

---

## Retraining

Retraining is triggered when drift report shows:
- `overall_drift_level = "high"` OR
- `max_psi >= 0.25`

To check the current retraining decision:
```bash
curl http://localhost:8000/api/v1/retraining/status
```

To manually trigger retraining:
```bash
curl -X POST http://localhost:8000/api/v1/retraining/trigger \
  -H "Content-Type: application/json" \
  -d '{"force": true, "reason": "manual test"}'
```

Retraining runs `scripts/07_train_model.py` and evaluates the Champion/Challenger gate.

---

## Custom Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predictions/custom \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "France",
    "away_team": "England",
    "match_date": "2026-08-01",
    "tournament": "Friendly",
    "neutral_venue": false
  }'
```

Response includes: prediction, probabilities, PCS, explanation, audit_event_id.

---

## Agent Query

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why did the model predict Brazil to win?"}'
```

Supported intents: latest_prediction, explain_prediction, model_accuracy,
model_limitations, drift_status, bias_fairness, dataset_summary,
confidence_explanation, context_availability, how_to_run, retraining_status,
provider_status, audit_trail, system_health.

---

## Audit Log

Local: `data/audit/audit_log.jsonl` (append-only JSONL)
Firestore: `audit_events` collection

Verify chain integrity:
```bash
curl http://localhost:8000/api/v1/audit/recent
```

---

## Docker Full Stack

```bash
docker compose up --build
```

First run initialises Airflow database and creates admin user.
Grafana auto-provisions the Prometheus datasource and PredictaGoal dashboard.

To stop:
```bash
docker compose down
```

To reset volumes:
```bash
docker compose down -v
```
