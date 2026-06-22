"""
Script 07 — Model Training.
Trains a RandomForest classifier on the feature dataset with a time-based split.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.features.feature_engineering import load_features_csv
from src.training.train_model import train

log = get_logger("07_train_model")


def main():
    print("\n" + "=" * 60)
    print("  MODEL TRAINING — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n  Loading feature dataset …")
    try:
        features_df = load_features_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)

    print(f"  Feature data loaded: {len(features_df)} rows")
    print(f"  Training model (RandomForestClassifier, 200 trees) …")
    print(f"  Train/test split: 80% / 20% (time-based)\n")

    try:
        report = train(features_df)
    except Exception as e:
        print(f"\n  ERROR during training: {e}")
        log.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)

    print("\n  --- Training Results ---")
    print(f"  Model type           : {report['model_type']}")
    print(f"  Train size           : {report['train_size']}")
    print(f"  Test size            : {report['test_size']}")
    print(f"  Test accuracy        : {report['accuracy']:.4f} ({report['accuracy']*100:.1f}%)")

    clf = report.get("classification_report", {})
    if clf:
        print("\n  Per-class metrics:")
        for label in ["home_win", "draw", "away_win"]:
            m = clf.get(label, {})
            print(
                f"    {label:<12} precision={m.get('precision',0):.2f}  "
                f"recall={m.get('recall',0):.2f}  f1={m.get('f1-score',0):.2f}  "
                f"support={m.get('support',0)}"
            )

    print(f"\n  Confusion matrix (home_win / draw / away_win):")
    for row in report.get("confusion_matrix", []):
        print(f"    {row}")

    print(f"\n  Model saved to      : models/artifacts/football_match_model.joblib")
    print(f"  Feature cols saved  : models/artifacts/feature_columns.json")
    print(f"  Training report     : models/reports/model_training_report.json")

    print("\n" + "=" * 60)
    print("  Training complete. Proceed to script 08.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
