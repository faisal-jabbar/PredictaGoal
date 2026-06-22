"""
Script 06 — Feature Engineering.
Generates leak-free features chronologically for every match.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.preprocessing.preprocess_matches import load_processed_csv
from src.features.feature_engineering import generate_features, FEATURE_COLS

log = get_logger("06_generate_features")


def main():
    print("\n" + "=" * 60)
    print("  FEATURE ENGINEERING — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n  Loading processed dataset …")
    try:
        processed_df = load_processed_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)

    print(f"  Processed data loaded: {len(processed_df)} rows")
    print("\n  Generating features (chronological, no leakage) …")
    print(f"  Rolling window size: 5 matches")

    try:
        features_df = generate_features(processed_df)
    except Exception as e:
        print(f"\n  ERROR during feature engineering: {e}")
        log.error(f"Feature engineering failed: {e}", exc_info=True)
        sys.exit(1)

    print("\n  --- Feature Engineering Summary ---")
    print(f"  Input rows           : {len(processed_df)}")
    print(f"  Output rows          : {len(features_df)}")
    print(f"  Feature columns ({len(FEATURE_COLS)}) :")
    for col in FEATURE_COLS:
        print(f"    - {col}")

    print(f"\n  Sample features (first 3 rows):")
    print(features_df[["date", "home_team", "away_team"] + FEATURE_COLS[:5]].head(3).to_string())

    print("\n  Features saved to data/processed/matches_features.csv")
    print("  Feature report saved to data/reports/feature_engineering_report.json")

    print("\n" + "=" * 60)
    print("  Feature engineering complete. Proceed to script 07.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
