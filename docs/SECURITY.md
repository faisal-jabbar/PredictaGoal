# PredictaGoal — Security Notes

## What Is Never Committed

| File/Path | Why |
|---|---|
| `.env` | Contains API keys and Firebase credentials |
| `secrets/` | Contains Firebase service account JSON |
| `*service_account*.json` | Firebase private key material |
| `data/raw/` | Raw dataset downloads |
| `data/processed/` | Derived data from raw |
| `models/artifacts/` | Trained model binaries |
| `mlruns/` | MLflow experiment data |
| `frontend/node_modules/` | npm packages |
| `frontend/dist/` | Build output |
| `logs/` | Server logs |

## What Is Committed

| File | Content |
|---|---|
| `.env.example` | Empty placeholder template only |
| `frontend/.env.example` | API base URL placeholder only |

## Runtime Security

- Firebase Admin SDK stays in Python backend only — never imported by frontend
- Frontend calls FastAPI, which calls Firebase server-side
- All public endpoints validate input against injection patterns
- Rate limiting: 60 req/min predictions, 30 req/min agent queries
- No tracebacks exposed in HTTP error responses (HTTP 400/500 with clean message)
- Audit trail is append-only — existing events cannot be modified

## External APIs

All external API integrations are optional.
If a key is missing, the provider returns:
```json
{"status": "disabled", "reason": "API_KEY not configured"}
```
The system continues running without it.

## GDPR Notes

- No real user data is collected in this project
- `user_preferences` stores team names and alert thresholds only
- All preference data deletable by removing the Firestore document
- Agent queries are logged with session_id only (no user identity)
