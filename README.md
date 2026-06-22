# PredictaGoal — AI Football Match Prediction Agent

> Three-phase ML system: data pipeline + intelligence dashboard + production agent.
> Predicts football match outcomes using historical data, Elo ratings, and ensemble ML.

---

## Architecture

```
[Kaggle Dataset] -> [Preprocessing] -> [Feature Engineering] -> [RandomForest Model]
                                                                        |
[FastAPI Backend] <- [Prediction Engine] <- [MLflow Registry] <- [Retraining Decision]
        |
[React Dashboard] + [Agent Query] + [Prometheus /metrics]
        |
[Grafana Dashboards] + [Airflow DAGs] + [Firestore + Audit Trail]
```

---

## Phase 01 — Core ML Pipeline

| Feature | Detail |
|---|---|
| Dataset | Kaggle `martj42/international-football-results-from-1872-to-2017` |
| Rows after cleaning | 49,431 matches |
| Model | RandomForest (200 trees, balanced weights, seed=42) |
| Test accuracy | 56.8% (time-based split) |
| Features | 14 leak-free signals (Elo, form, H2H, goals avg, venue) |
| Storage | Firestore + local JSON fallback |

## Phase 02 — Intelligence Dashboard

- Prediction Confidence Score (PCS) with tier labels
- SHAP + RF-importance explanations with natural language
- Contextual intelligence (dataset-available fields only)
- PSI + KS-test drift detection
- Bias/fairness reporting by outcome class
- FastAPI REST backend + React/Vite/TailwindCSS/Recharts dashboard

## Phase 03 — Production Agent

- Airflow DAGs: daily pipeline, retraining, and monitoring
- MLflow experiment tracking + model versioning + registry
- Real drift-triggered retraining decision logic (PSI >= 0.25 or HIGH drift)
- Champion/Challenger model promotion rules
- Conversational agent interface (14 intents, rule-based, optional LLM)
- User preferences + alert system (local + Firestore, optional SMTP)
- SHA-256 hash-chained immutable audit trail
- Multi-source provider architecture (Kaggle, weather via Open-Meteo free, fixtures/injury optional)
- Input validation + adversarial checks + rate limiting (FR18)
- Prometheus metrics endpoint + Grafana dashboard provisioning
- Docker Compose full-stack deployment

---

## Quick Start

### 1. Environment Setup

```bash
# Copy and fill in your credentials
copy .env.example .env

# Install Python dependencies
python -m pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Phase 01 — Core Pipeline

```bash
python scripts/01_check_environment.py
python scripts/02_test_firebase.py
python scripts/03_verify_kaggle.py
python scripts/04_download_dataset.py
python scripts/05_preprocess_data.py
python scripts/06_generate_features.py
python scripts/07_train_model.py
python scripts/08_run_prediction.py
```

### 3. Phase 02 — Intelligence Reports

```bash
python scripts/09_generate_explanations.py
python scripts/10_calculate_confidence.py
python scripts/11_generate_drift_report.py
python scripts/12_generate_bias_report.py
python scripts/13_verify_phase02.py
```

### 4. Phase 03 — Production Setup

```bash
python scripts/14_run_airflow_pipeline_check.py
python scripts/15_run_mlflow_check.py
python scripts/16_run_monitoring_check.py
python scripts/17_run_agent_query_check.py
python scripts/18_run_phase03_verification.py
```

### 5. Run the System

**Backend (FastAPI):**
```bash
python -m uvicorn src.api.main:app --reload
# API docs:   http://localhost:8000/docs
# Prometheus: http://localhost:8000/metrics
```

**Frontend (React):**
```bash
cd frontend && npm run dev
# Dashboard: http://localhost:5173
```

**MLflow UI:**
```bash
mlflow ui --host 127.0.0.1 --port 5000
```

**Docker full-stack:**
```bash
docker compose up --build
# Backend:    http://localhost:8000
# Frontend:   http://localhost:8080
# MLflow:     http://localhost:5000
# Airflow:    http://localhost:8081   (admin/admin)
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000   (admin/predictagoal)
```

**Airflow (requires apache-airflow):**
```bash
pip install apache-airflow
set AIRFLOW_HOME=%cd%\airflow
airflow standalone
```

---

## .env Configuration

```env
FIREBASE_SERVICE_ACCOUNT_PATH=secrets/firebase-service-account.json
KAGGLE_API_TOKEN=your_kaggle_token

# Optional Phase 03 providers
FOOTBALL_API_KEY=
WEATHER_API_KEY=
INJURY_API_KEY=

# Optional email alerts
ENABLE_EMAIL_ALERTS=false
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=

# Optional LLM agent
OPENAI_API_KEY=
ENABLE_LLM_AGENT=false
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | System health + Firebase status |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/v1/summary` | Dataset + model summary |
| GET | `/api/v1/predictions/sample` | Sample Brazil vs Argentina prediction |
| POST | `/api/v1/predictions/custom` | Custom match prediction |
| POST | `/api/v1/agent/query` | Conversational agent query |
| GET | `/api/v1/agent/capabilities` | Supported agent intents |
| GET | `/api/v1/system/status` | Full system health report |
| GET | `/api/v1/providers/status` | External provider status |
| GET | `/api/v1/retraining/status` | Retraining decision |
| POST | `/api/v1/retraining/trigger` | Manual trigger (force=true required) |
| GET | `/api/v1/model/version` | Current model version |
| GET | `/api/v1/audit/recent` | Recent audit events |
| GET | `/api/v1/alerts/recent` | Recent alerts |
| POST | `/api/v1/preferences` | Save user preferences |
| GET | `/api/v1/preferences/{user_id}` | Get user preferences |

---

## Security Notes

- `.env` is gitignored — never committed
- `secrets/` is gitignored — Firebase key stays local
- Firebase Admin SDK never exposed to frontend
- All external API keys optional
- Input validation + injection sanitisation on all endpoints
- Rate limiting on prediction and agent endpoints

---

## Known Limitations

- Draw accuracy ~30% due to class imbalance
- External providers (fixtures, injuries) require API keys not included
- Weather uses Open-Meteo (free) but needs venue lat/lon not in dataset
- Airflow installed separately (`pip install apache-airflow`)
- Docker requires Docker Desktop on Windows
- LLM agent requires `OPENAI_API_KEY` + `ENABLE_LLM_AGENT=true`
- Model accuracy ceiling 55-70% — football has irreducible randomness

---

## Troubleshooting (Windows PowerShell)

```powershell
# Wrong pip version: always use
python -m pip install <package>

# Port 8000 in use:
netstat -ano | findstr :8000

# Firebase not found: check .env path matches actual file location
```

---

*For analytical purposes only. Not financial or betting advice.*
