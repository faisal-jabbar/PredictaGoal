"""Script 10 — Calculate Prediction Confidence Score (FR11)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.confidence.confidence_calibration import run_confidence_report
from src.utils.file_utils import load_json
from src.config import settings

log = get_logger("10_calculate_confidence")

def main():
    print("\n" + "="*60)
    print("  CONFIDENCE CALIBRATION — PredictaGoal Phase 02")
    print("="*60)

    pred_path = os.path.join(settings.DATA_REPORTS_DIR, "sample_prediction.json")
    if not os.path.isfile(pred_path):
        print("\n  ERROR: Run scripts/08_predict_sample.py first."); sys.exit(1)

    pred = load_json(pred_path)
    print(f"\n  Match    : {pred['home_team']} vs {pred['away_team']}")
    print(f"  Probabilities: {pred['probabilities']}")

    report = run_confidence_report(pred)

    print(f"\n  --- Confidence Result ---")
    print(f"  PCS              : {report['pcs']:.4f}")
    print(f"  Confidence Tier  : {report['confidence_tier']}")
    print(f"  Margin score     : {report['margin_score']:.4f}")
    print(f"  Top-2 margin     : {report['top2_margin']:.4f}")
    print(f"  Entropy          : {report['entropy']:.4f}")
    print(f"  Feature penalty  : {report['feature_penalty']:.4f}")
    print(f"\n  Note: {report['confidence_note']}")
    print(f"\n  Report saved: data/reports/confidence_report.json")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
