"""Script 12 — Bias & Fairness Detection Report (FR17)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.bias.bias_detection import run_bias_report
from src.training.train_model import load_model
from src.features.feature_engineering import load_features_csv

log = get_logger("12_generate_bias_report")

def main():
    print("\n" + "="*60)
    print("  BIAS & FAIRNESS REPORT — PredictaGoal Phase 02")
    print("="*60)

    try:
        model = load_model()
        features_df = load_features_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}"); sys.exit(1)

    print(f"\n  Evaluating on test set (last 20% by date) ...")
    report = run_bias_report(model, features_df)

    print(f"\n  --- Bias Report Summary ---")
    print(f"  Overall accuracy   : {report['overall_accuracy']:.4f} ({report['overall_accuracy']*100:.1f}%)")
    print(f"  Test set size      : {report['test_set_size']}")
    print(f"\n  Accuracy by class:")
    for cls, acc in report["accuracy_by_class"].items():
        print(f"    {cls:<12} : {acc:.4f} ({(acc or 0)*100:.1f}%)")
    print(f"\n  Prediction distribution:")
    for cls, pct in report["prediction_distribution"].items():
        actual = report["actual_distribution"].get(cls, 0)
        print(f"    {cls:<12} : predicted={pct:.1%}  actual={actual:.1%}")
    print(f"\n  Known issue: {report['known_issue'][:120]}...")
    print(f"\n  Report saved: data/reports/bias_report.json")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
