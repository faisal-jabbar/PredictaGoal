"""
Script 04 — Dataset Download.
Downloads the Kaggle football dataset via KaggleHub.

Supports KAGGLE_API_TOKEN from .env — no kaggle.json required.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.config import settings
from src.ingestion.kaggle_loader import download_dataset

log = get_logger("04_download_dataset")


def main():
    print("\n" + "=" * 60)
    print("  DATASET DOWNLOAD — AI Football Match Prediction Agent")
    print("=" * 60)
    print(f"\n  Dataset slug : {settings.KAGGLE_DATASET}")

    # Show auth status (never print the token itself)
    if settings.kaggle_token_available():
        print("  Kaggle auth  : API token detected.")
    else:
        print("  Kaggle auth  : KAGGLE_API_TOKEN not set — will try ~/.kaggle/kaggle.json")

    print("\n  Downloading via KaggleHub …\n")

    try:
        df = download_dataset()
    except Exception as exc:
        print(f"\n  ERROR: {exc}")
        print("\n  Troubleshooting:")
        print("    1. Ensure KAGGLE_API_TOKEN is set in .env")
        print("    2. Or place kaggle.json in ~/.kaggle/  (legacy method)")
        print("    3. Run: pip install kagglehub")
        log.error(f"Dataset download failed: {exc}", exc_info=True)
        sys.exit(1)

    print("\n  --- Dataset Summary ---")
    print(f"  Shape    : {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Columns  : {list(df.columns)}")
    if "date" in df.columns:
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"\n  Null counts:")
    for col, cnt in df.isnull().sum().items():
        if cnt > 0:
            print(f"    {col}: {cnt}")

    print(f"\n  First 3 rows:")
    print(df.head(3).to_string())

    print("\n  Raw CSV saved  : data/raw/matches_raw.csv")
    print("  Summary saved  : data/reports/dataset_summary.json")

    print("\n" + "=" * 60)
    print("  Download complete. Proceed to script 05.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
