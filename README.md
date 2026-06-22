# AI Football Match Prediction Agent — Phase 01

A Python-first ML pipeline that predicts international football match outcomes
(home win / draw / away win) using historical Kaggle data, scikit-learn, and
optional Firebase Firestore storage.

---

## What Phase 01 Implements

| Module | Description |
|---|---|
| FR1 — Match Data Input | Downloads dataset via KaggleHub, inspects schema |
| FR2 — Data Preprocessing | Cleans data, validates scores, creates outcome labels |
| FR3 — Feature Engineering | Rolling form, goals avg, Elo rating, H2H stats (no leakage) |
| FR4 — Basic Prediction Engine | Load model, generate features, return prediction + probabilities |
| FR5 — Model Training | RandomForest, time-based split, accuracy + classification report |
| FR8 — Results Storage | Firebase Firestore or local JSON fallback |
| FR9 — Prototype Output | CLI scripts showing full system status and predictions |

## What is NOT in Phase 01

- Frontend / dashboard (React, etc.)
- SHAP / explainability
- LLM-generated explanations
- Drift detection
- Advanced ensemble models
- Multi-tournament orchestration
- Alerts / notifications

---

## Folder Structure

```
football-match-predictions/
├── data/
│   ├── raw/                  # Raw CSV from Kaggle
│   ├── processed/            # Cleaned CSV + features CSV
│   └── reports/              # JSON quality/prediction reports
├── models/
│   ├── artifacts/            # Trained model (.joblib) + feature list
│   └── reports/              # Training run reports
├── logs/                     # Daily pipeline log files
├── src/
│   ├── config/settings.py    # Environment-based configuration
│   ├── database/             # Firebase client + Firestore helpers + local fallback
│   ├── ingestion/            # KaggleHub dataset download
│   ├── preprocessing/        # Data cleaning and outcome labelling
│   ├── features/             # Feature engineering (Elo, rolling form, H2H)
│   ├── training/             # Model training and evaluation
│   ├── prediction/           # Prediction engine
│   └── utils/                # Logging and file helpers
├── scripts/                  # Numbered CLI scripts (run in order)
├── docs/                     # FRS document
├── .env.example              # Environment variable template
├── requirements.txt
└── README.md
```

---

## Python Environment Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

**Python 3.9 or higher is recommended.**

---

## Firebase Setup (Optional)

Firebase is optional. The pipeline works without it using local JSON fallback.

### Option A — Service Account JSON (recommended)

1. Go to [Firebase Console](https://console.firebase.google.com/) → Project Settings → Service Accounts.
2. Click **Generate new private key** → download the JSON file.
3. Place it anywhere on your machine (e.g. `firebase_service_account.json`).
4. Copy `.env.example` to `.env` and set:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=C:/path/to/firebase_service_account.json
```

### Option B — Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n
```

> Note: Replace actual newlines in the private key with `\n` as a single line.

### Firestore Rules (for testing)

In Firebase Console → Firestore Database → Rules:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true; // Change this before production
    }
  }
}
```

---

## Kaggle Dataset Setup

The dataset used is:  
`martj42/international-football-results-from-1872-to-2017`

### Authentication — New API Token Method (Recommended)

This project supports the **new Kaggle API token format** (`KGAT_...`).  
No `kaggle.json` file is required.

1. Go to [kaggle.com/settings](https://www.kaggle.com/settings) → **API** → **Create New Token**
2. Copy the token string (it starts with `KGAT_`)
3. Add it to your `.env` file:

```env
KAGGLE_API_TOKEN=KGAT_your_token_here
```

The project reads this via `python-dotenv` and configures KaggleHub automatically.  
The token is **never printed** in logs or output.

### Authentication — Legacy Method (Fallback)

If the new token doesn't work with your KaggleHub version:

1. Go to [kaggle.com/settings](https://www.kaggle.com/settings) → **API** → **Create New Token**
2. Download the `kaggle.json` file
3. Place it at:
   - Windows: `C:\Users\<user>\.kaggle\kaggle.json`
   - Linux/Mac: `~/.kaggle/kaggle.json`

---

## Run Order

Run scripts in this exact order:

```bash
python scripts/01_check_environment.py
python scripts/02_setup_database.py
python scripts/03_test_firebase.py
python scripts/04_download_dataset.py
python scripts/05_preprocess_data.py
python scripts/06_generate_features.py
python scripts/07_train_model.py
python scripts/08_predict_sample.py
```

---

## Expected Outputs

After running all scripts:

| File | Description |
|---|---|
| `data/raw/matches_raw.csv` | Original dataset copy |
| `data/processed/matches_processed.csv` | Cleaned dataset with outcome labels |
| `data/processed/matches_features.csv` | Feature-engineered dataset |
| `data/reports/dataset_summary.json` | Dataset schema summary |
| `data/reports/data_quality_report.json` | Preprocessing quality metrics |
| `data/reports/feature_engineering_report.json` | Feature generation summary |
| `data/reports/sample_prediction.json` | Brazil vs Argentina prediction |
| `models/artifacts/football_match_model.joblib` | Trained model |
| `models/artifacts/feature_columns.json` | Feature column list |
| `models/reports/model_training_report.json` | Accuracy + classification report |
| `logs/YYYYMMDD_pipeline.log` | Full run log |

---

## Troubleshooting

### `ModuleNotFoundError`
Run `pip install -r requirements.txt`

### `kagglehub` download fails
- Ensure `~/.kaggle/kaggle.json` exists
- Or set `KAGGLE_USERNAME` / `KAGGLE_KEY` in `.env`

### Firebase connection fails
- Check credentials are correct
- Check Firestore is enabled in Firebase Console
- The pipeline will continue with local fallback — no crash

### `FileNotFoundError` on script N
- Run the previous scripts in order first
- Each script depends on the output of the one before it

### Low model accuracy
- This is expected for multi-class football prediction
- Typical accuracy: 50–60% (football is inherently unpredictable)
- Results are reported honestly without manipulation

---

## Firestore Collections (Phase 01)

| Collection | Contents |
|---|---|
| `data_quality_reports` | Preprocessing quality metrics |
| `model_runs` | Training run summaries |
| `sample_predictions` | Individual match predictions |
| `pipeline_logs` | Pipeline event logs |
| `dataset_summaries` | Dataset schema metadata |
