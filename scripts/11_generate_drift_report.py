"""Script 11 — Feature Drift Detection Report (FR12)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger
from src.drift.drift_detection import run_drift_report
from src.features.feature_engineering import load_features_csv

log = get_logger("11_generate_drift_report")

def main():
    print("\n" + "="*60)
    print("  DRIFT DETECTION — PredictaGoal Phase 02")
    print("="*60)

    try:
        features_df = load_features_csv()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}"); sys.exit(1)

    print(f"\n  Dataset: {len(features_df)} rows")
    print(f"  Baseline: first 80% | Recent: last 20%")
    print(f"  Analysing {14} features with PSI + KS test ...\n")

    report = run_drift_report(features_df)

    print(f"  --- Drift Summary ---")
    print(f"  Overall drift level  : {report['overall_drift_level'].upper()}")
    print(f"  Features checked     : {report['features_checked']}")
    print(f"  Drifted features     : {report['drifted_count']} — {report['drifted_features'] or 'none'}")
    print(f"  Max PSI              : {report['max_psi']:.4f}")
    print(f"\n  Baseline: {report['baseline_period']['from']} to {report['baseline_period']['to']}")
    print(f"  Recent  : {report['recent_period']['from']} to {report['recent_period']['to']}")
    print(f"\n  Note: {report['notes']}")
    print(f"\n  Report saved: data/reports/drift_report.json")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
