"""
FR17 — Bias & Fairness Detection.
Analyses model performance by class, tournament, and venue type.
Only uses attributes present in the dataset — no demographic claims.
"""
import os
from datetime import datetime
from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from src.config import settings
from src.database import firestore_service
from src.features.feature_engineering import FEATURE_COLS
from src.utils.file_utils import save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

BIAS_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "bias_report.json")

LABEL_MAP = {0: "home_win", 1: "draw", 2: "away_win"}
REVERSE_LABEL = {"home_win": 0, "draw": 1, "away_win": 2}
TOP_TOURNAMENTS = 8


def run_bias_report(model, features_df: pd.DataFrame) -> Dict[str, Any]:
    df = features_df.dropna(subset=FEATURE_COLS + ["outcome"]).copy()
    df = df.sort_values("date").reset_index(drop=True)
    split = int(len(df) * 0.80)
    test_df = df.iloc[split:].copy()

    X_test = test_df[FEATURE_COLS].values
    y_true_labels = test_df["outcome"].values
    y_true = np.array([REVERSE_LABEL.get(o, -1) for o in y_true_labels])

    mask = y_true >= 0
    X_test, y_true, y_true_labels = X_test[mask], y_true[mask], y_true_labels[mask]

    y_pred = model.predict(X_test)
    y_pred_labels = np.array([LABEL_MAP[p] for p in y_pred])

    overall_acc = float(round(accuracy_score(y_true, y_pred), 4))
    log.info(f"Bias report — overall test accuracy: {overall_acc:.4f}")

    # Accuracy by class
    acc_by_class = {}
    for label in ["home_win", "draw", "away_win"]:
        mask_c = y_true_labels == label
        if mask_c.sum() == 0:
            acc_by_class[label] = None
        else:
            acc_by_class[label] = float(round(accuracy_score(y_true[mask_c], y_pred[mask_c]), 4))

    # Prediction distribution
    pred_counts = {l: int((y_pred_labels == l).sum()) for l in ["home_win", "draw", "away_win"]}
    actual_counts = {l: int((y_true_labels == l).sum()) for l in ["home_win", "draw", "away_win"]}
    n = len(y_pred_labels)
    pred_dist = {k: round(v / n, 4) for k, v in pred_counts.items()}
    actual_dist = {k: round(v / n, 4) for k, v in actual_counts.items()}

    # Accuracy by neutral vs home venue
    acc_by_venue = {}
    if "neutral" in test_df.columns:
        for venue_val, label in [(True, "neutral"), (False, "home_ground")]:
            vm = test_df["neutral"].values[mask] == venue_val
            if vm.sum() > 0:
                acc_by_venue[label] = float(round(accuracy_score(y_true[vm], y_pred[vm]), 4))

    # Accuracy by top tournaments
    acc_by_tournament = {}
    if "tournament" in test_df.columns:
        t_series = test_df["tournament"].values[mask]
        unique_t, t_counts = np.unique(t_series, return_counts=True)
        top_t = [t for t, c in sorted(zip(unique_t, t_counts), key=lambda x: -x[1])[:TOP_TOURNAMENTS]]
        for t in top_t:
            tm = t_series == t
            if tm.sum() >= 10:
                acc_by_tournament[t] = {
                    "accuracy": float(round(accuracy_score(y_true[tm], y_pred[tm]), 4)),
                    "sample_size": int(tm.sum()),
                }

    # Draw analysis
    draw_recall = acc_by_class.get("draw", 0) or 0
    draw_note = (
        f"Draw recall is {draw_recall:.1%}, which is substantially below home_win ({acc_by_class.get('home_win',0):.1%}). "
        "This is a known challenge in football prediction — draws are inherently difficult to predict "
        "because they often result from evenly matched teams or defensive play patterns not captured by aggregate statistics."
    ) if draw_recall < 0.45 else "Draw prediction is performing at an acceptable level."

    report = {
        "overall_accuracy": overall_acc,
        "test_set_size": int(len(y_true)),
        "accuracy_by_class": acc_by_class,
        "prediction_distribution": pred_dist,
        "actual_distribution": actual_dist,
        "accuracy_by_venue": acc_by_venue,
        "accuracy_by_tournament": acc_by_tournament,
        "known_issue": draw_note,
        "fairness_notes": (
            "The Kaggle international football results dataset does not include demographic attributes. "
            "Bias analysis is limited to football-specific groupings: outcome class, tournament type, and venue. "
            "No claims are made about demographic fairness."
        ),
        "generated_at": datetime.utcnow().isoformat(),
    }

    save_json(report, BIAS_REPORT_PATH)
    log.info(f"Bias report saved: {BIAS_REPORT_PATH}")

    safe_report = {
        k: v for k, v in report.items()
        if k not in ("accuracy_by_tournament", "accuracy_by_venue")
    }
    safe_report["accuracy_by_tournament_keys"] = ", ".join(list(acc_by_tournament.keys())[:5])
    firestore_service.write_document(
        "bias_reports", "latest", safe_report, fallback_path=BIAS_REPORT_PATH
    )

    return report
