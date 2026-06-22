"""Script 09 — Generate prediction explanations (FR6)."""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.preprocessing.preprocess_matches import load_processed_csv
from src.prediction.predict import _build_features
from src.training.train_model import load_model, load_feature_columns
from src.explanation.explanation_service import generate_full_explanation
from src.utils.file_utils import load_json
from src.config import settings
import pandas as pd

log = get_logger("09_generate_explanations")

def main():
    print("\n" + "="*60)
    print("  EXPLANATION GENERATOR — PredictaGoal Phase 02")
    print("="*60)

    pred_path = os.path.join(settings.DATA_REPORTS_DIR, "sample_prediction.json")
    conf_path = os.path.join(settings.DATA_REPORTS_DIR, "confidence_report.json")

    if not os.path.isfile(pred_path):
        print("\n  ERROR: Run scripts/08_predict_sample.py first."); sys.exit(1)
    if not os.path.isfile(conf_path):
        print("\n  ERROR: Run scripts/10_calculate_confidence.py first."); sys.exit(1)

    pred = load_json(pred_path)
    conf = load_json(conf_path)

    print("\n  Loading model and historical data ...")
    model = load_model()
    feature_cols = load_feature_columns()
    historical_df = load_processed_csv()

    feature_values = _build_features(
        home_team=pred["home_team"],
        away_team=pred["away_team"],
        match_date=pd.Timestamp(pred["match_date"]),
        historical_df=historical_df,
        neutral=pred.get("neutral_venue", False),
    )

    print(f"  Generating explanation (SHAP if available, RF fallback) ...")
    report = generate_full_explanation(model, feature_cols, feature_values, pred, conf)

    print(f"\n  Method used   : {report['method']}")
    print(f"  SHAP available: {report['shap_available']}")
    print(f"\n  Explanation:\n  {report['explanation_text']}")
    print(f"\n  Top features:")
    for f in (report.get("top_features") or [])[:5]:
        print(f"    {f['display_name']:<30} importance={f['importance']:.4f}  value={f['feature_value']:.3f}")

    print(f"\n  Report saved: data/reports/explanation_report.json")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
