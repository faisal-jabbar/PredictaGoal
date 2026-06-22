"""
FR1 — Match Data Input Module.
Downloads the Kaggle dataset via KaggleHub, discovers CSV files, and saves a raw copy.

Supports the new Kaggle API token format via KAGGLE_API_TOKEN in .env.
Does NOT require a legacy kaggle.json file.
"""
import glob
import os
import shutil
from datetime import datetime
from typing import Dict, Any

import pandas as pd

from src.config import settings
from src.database import firestore_service
from src.utils.file_utils import ensure_dir, save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

RAW_CSV_DEST = os.path.join(settings.DATA_RAW_DIR, "matches_raw.csv")
SUMMARY_PATH = os.path.join(settings.DATA_REPORTS_DIR, "dataset_summary.json")


def _configure_kaggle_auth() -> bool:
    """
    Configures KaggleHub authentication from KAGGLE_API_TOKEN env var.
    Returns True if a token was detected, False otherwise.
    """
    token = settings.KAGGLE_API_TOKEN
    if not token:
        log.warning("KAGGLE_API_TOKEN not set. Kaggle auth may fall back to ~/.kaggle/kaggle.json.")
        return False

    log.info("Kaggle API token detected.")

    # KaggleHub reads KAGGLE_KEY env var (the token itself) for API token auth.
    # We set it so KaggleHub can pick it up without a kaggle.json file.
    os.environ["KAGGLE_KEY"] = token

    # KAGGLE_USERNAME is required alongside KAGGLE_KEY by the underlying kaggle SDK.
    # For API token auth the username is embedded in the token prefix (KGAT_ tokens
    # are userless bearer tokens) — set a placeholder so the SDK doesn't error.
    if not os.environ.get("KAGGLE_USERNAME"):
        os.environ["KAGGLE_USERNAME"] = "user"

    return True


def download_dataset() -> pd.DataFrame:
    log.info(f"Downloading Kaggle dataset: {settings.KAGGLE_DATASET}")

    token_ok = _configure_kaggle_auth()

    try:
        import kagglehub
        dataset_path = kagglehub.dataset_download(settings.KAGGLE_DATASET)
        log.info(f"KaggleHub download path: {dataset_path}")
    except Exception as exc:
        _log_kaggle_auth_hint(exc, token_ok)
        raise

    csv_files = glob.glob(os.path.join(dataset_path, "**", "*.csv"), recursive=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {dataset_path}")

    log.info(f"CSV files discovered: {[os.path.basename(f) for f in csv_files]}")

    # Prefer the results file if multiple CSVs exist
    primary = next(
        (f for f in csv_files if "results" in os.path.basename(f).lower()),
        csv_files[0],
    )
    log.info(f"Selected CSV: {os.path.basename(primary)}")

    df = pd.read_csv(primary)
    log.info(f"Dataset loaded — shape: {df.shape}")
    log.info(f"Columns: {list(df.columns)}")

    ensure_dir(settings.DATA_RAW_DIR)
    shutil.copy2(primary, RAW_CSV_DEST)
    log.info(f"Raw copy saved to: {RAW_CSV_DEST}")

    summary = _build_summary(df, primary)
    save_json(summary, SUMMARY_PATH)
    log.info(f"Dataset summary saved: {SUMMARY_PATH}")

    firestore_service.write_document(
        settings.COLLECTION_DATASET_SUMMARIES,
        "latest",
        summary,
        fallback_path=SUMMARY_PATH,
    )

    return df


def _build_summary(df: pd.DataFrame, source_path: str) -> Dict[str, Any]:
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    date_range = {}
    if date_col:
        dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
        date_range = {"from": str(dates.min().date()), "to": str(dates.max().date())}

    return {
        "source_file": os.path.basename(source_path),
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": {k: int(v) for k, v in df.isnull().sum().items()},
        "date_range": date_range,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _log_kaggle_auth_hint(exc: Exception, token_present: bool) -> None:
    log.error(f"KaggleHub download failed: {exc}")
    if not token_present:
        log.error(
            "No KAGGLE_API_TOKEN found. To fix:\n"
            "  1. Go to https://www.kaggle.com/settings -> API -> Create New Token\n"
            "  2. Copy the token value (starts with KGAT_)\n"
            "  3. Add to .env: KAGGLE_API_TOKEN=<your-token>"
        )
    else:
        log.error(
            "KAGGLE_API_TOKEN was detected but KaggleHub still failed.\n"
            "This may mean KaggleHub requires legacy credentials (kaggle.json).\n"
            "If so, please:\n"
            "  1. Go to https://www.kaggle.com/settings -> API -> Create New Token\n"
            "  2. Download the kaggle.json file\n"
            "  3. Place it at: ~/.kaggle/kaggle.json  (Linux/Mac) or\n"
            "                  C:\\Users\\<user>\\.kaggle\\kaggle.json  (Windows)\n"
            "  4. Run script 04 again"
        )


def load_raw_csv() -> pd.DataFrame:
    if not os.path.isfile(RAW_CSV_DEST):
        raise FileNotFoundError(
            f"Raw CSV not found at {RAW_CSV_DEST}. Run scripts/04_download_dataset.py first."
        )
    df = pd.read_csv(RAW_CSV_DEST)
    log.info(f"Raw CSV loaded from cache — shape: {df.shape}")
    return df
