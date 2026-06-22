"""
Script 05 — Data Preprocessing.
Cleans raw match data, validates scores, creates outcome labels.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.ingestion.kaggle_loader import load_raw_csv
from src.preprocessing.preprocess_matches import preprocess

log = get_logger("05_preprocess_data")


def main():
    print("\n" + "=" * 60)
    print("  DATA PREPROCESSING — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n  Loading raw dataset …")
    try:
        raw_df = load_raw_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)

    print(f"  Raw data loaded: {raw_df.shape[0]} rows, {raw_df.shape[1]} columns")
    print("\n  Running preprocessing pipeline …")

    try:
        processed_df = preprocess(raw_df)
    except Exception as e:
        print(f"\n  ERROR during preprocessing: {e}")
        log.error(f"Preprocessing failed: {e}", exc_info=True)
        sys.exit(1)

    print("\n  --- Preprocessing Summary ---")
    print(f"  Input rows           : {len(raw_df)}")
    print(f"  Output rows          : {len(processed_df)}")
    print(f"  Rows removed         : {len(raw_df) - len(processed_df)}")
    print(f"  Columns              : {list(processed_df.columns)}")
    if "outcome" in processed_df.columns:
        print(f"  Outcome distribution :\n{processed_df['outcome'].value_counts().to_string()}")
    print(f"  Date range           : {processed_df['date'].min().date()} to {processed_df['date'].max().date()}")

    print("\n  Processed data saved to data/processed/matches_processed.csv")
    print("  Data quality report saved to data/reports/data_quality_report.json")

    print("\n" + "=" * 60)
    print("  Preprocessing complete. Proceed to script 06.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
