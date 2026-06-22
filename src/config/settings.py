import os
from pathlib import Path
from dotenv import load_dotenv

_root = Path(__file__).resolve().parent.parent.parent
_env_file = _root / ".env"
load_dotenv(dotenv_path=_env_file)

# Firebase
FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")

# Resolve service account path relative to project root if not absolute
if FIREBASE_SERVICE_ACCOUNT_PATH and not os.path.isabs(FIREBASE_SERVICE_ACCOUNT_PATH):
    FIREBASE_SERVICE_ACCOUNT_PATH = str(_root / FIREBASE_SERVICE_ACCOUNT_PATH)

# Kaggle — new API token format
KAGGLE_API_TOKEN: str = os.getenv("KAGGLE_API_TOKEN", "")

# Firestore collections
COLLECTION_DATA_QUALITY = "data_quality_reports"
COLLECTION_MODEL_RUNS = "model_runs"
COLLECTION_PREDICTIONS = "sample_predictions"
COLLECTION_LOGS = "pipeline_logs"
COLLECTION_DATASET_SUMMARIES = "dataset_summaries"

# Local paths
DATA_RAW_DIR: str = str(_root / "data" / "raw")
DATA_PROCESSED_DIR: str = str(_root / "data" / "processed")
DATA_REPORTS_DIR: str = str(_root / "data" / "reports")
MODELS_ARTIFACTS_DIR: str = str(_root / "models" / "artifacts")
MODELS_REPORTS_DIR: str = str(_root / "models" / "reports")
LOGS_DIR: str = str(_root / "logs")

# Dataset
KAGGLE_DATASET = "martj42/international-football-results-from-1872-to-2017"

# Model
RANDOM_SEED = 42
ROLLING_WINDOW = 5


def firebase_credentials_available() -> bool:
    if FIREBASE_SERVICE_ACCOUNT_PATH and os.path.isfile(FIREBASE_SERVICE_ACCOUNT_PATH):
        return True
    return bool(FIREBASE_PROJECT_ID and FIREBASE_CLIENT_EMAIL and FIREBASE_PRIVATE_KEY)


def kaggle_token_available() -> bool:
    return bool(KAGGLE_API_TOKEN)
