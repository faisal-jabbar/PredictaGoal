"""
Script 08 — Sample Prediction.
Loads the trained model and generates a sample prediction for Brazil vs Argentina.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.preprocessing.preprocess_matches import load_processed_csv
from src.prediction.predict import run_sample_prediction, predict_match

log = get_logger("08_predict_sample")


def main():
    print("\n" + "=" * 60)
    print("  SAMPLE PREDICTION — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n  Loading historical match data …")
    try:
        historical_df = load_processed_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)

    print(f"  Historical data loaded: {len(historical_df)} matches")

    # Default sample prediction
    print("\n  Running sample prediction: Brazil vs Argentina (2017-06-01) …\n")
    try:
        result = run_sample_prediction(historical_df)
    except Exception as e:
        print(f"\n  ERROR during prediction: {e}")
        log.error(f"Prediction failed: {e}", exc_info=True)
        sys.exit(1)

    print("  --- Prediction Result ---")
    print(json.dumps(result, indent=4))

    print("\n  Sample prediction saved to data/reports/sample_prediction.json")

    # Interactive extra prediction — only when running in a real terminal
    if sys.stdin.isatty():
        print("\n" + "-" * 60)
        print("  Run another prediction? (press Enter to skip)")
        try:
            home = input("  Home team  : ").strip()
            away = input("  Away team  : ").strip()
            date = input("  Match date (YYYY-MM-DD): ").strip()

            if home and away and date:
                result2 = predict_match(
                    home_team=home,
                    away_team=away,
                    match_date=date,
                    historical_df=historical_df,
                )
                print("\n  --- Prediction Result ---")
                print(json.dumps(result2, indent=4))
        except (KeyboardInterrupt, EOFError):
            pass

    print("\n" + "=" * 60)
    print("  Phase 01 pipeline complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
