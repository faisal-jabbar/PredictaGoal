"""
FR5 — Model Training Module.
Trains a classifier to predict home_win / draw / away_win.
Uses a time-based train/test split to avoid leakage.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

from src.config import settings
from src.database import firestore_service
from src.features.feature_engineering import FEATURE_COLS
from src.utils.file_utils import save_json, ensure_dir
from src.utils.logger import get_logger

log = get_logger(__name__)

MODEL_PATH = os.path.join(settings.MODELS_ARTIFACTS_DIR, "football_match_model.joblib")
FEATURE_COLS_PATH = os.path.join(settings.MODELS_ARTIFACTS_DIR, "feature_columns.json")
TRAINING_REPORT_PATH = os.path.join(settings.MODELS_REPORTS_DIR, "model_training_report.json")

LABEL_ORDER = ["home_win", "draw", "away_win"]
TRAIN_RATIO = 0.8


def train(features_df: pd.DataFrame) -> Dict[str, Any]:
    log.info("Starting model training.")

    df = features_df.dropna(subset=FEATURE_COLS + ["outcome"]).copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Encode outcome
    df["outcome_label"] = df["outcome"].map({"home_win": 0, "draw": 1, "away_win": 2})

    X = df[FEATURE_COLS].values
    y = df["outcome_label"].values

    split_idx = int(len(df) * TRAIN_RATIO)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    log.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    model = _train_random_forest(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    clf_report = classification_report(
        y_test, y_pred,
        target_names=LABEL_ORDER,
        output_dict=True,
        zero_division=0,
    )
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist()

    log.info(f"Test accuracy: {acc:.4f}")
    log.info(f"\n{classification_report(y_test, y_pred, target_names=LABEL_ORDER, zero_division=0)}")

    # Save artifacts
    ensure_dir(settings.MODELS_ARTIFACTS_DIR)
    ensure_dir(settings.MODELS_REPORTS_DIR)

    joblib.dump(model, MODEL_PATH)
    log.info(f"Model saved: {MODEL_PATH}")

    with open(FEATURE_COLS_PATH, "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)
    log.info(f"Feature columns saved: {FEATURE_COLS_PATH}")

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Firestore does not allow nested arrays — flatten confusion matrix to a string for Firestore,
    # keep the full nested version in the local JSON report.
    cm_str = str(cm)

    report: Dict[str, Any] = {
        "run_id": run_id,
        "model_type": type(model).__name__,
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "accuracy": float(acc),
        "classification_report": clf_report,
        "confusion_matrix": cm,          # nested list — for local JSON only
        "label_order": LABEL_ORDER,
        "feature_columns": FEATURE_COLS,
        "model_path": MODEL_PATH,
        "trained_at": datetime.utcnow().isoformat(),
    }

    save_json(report, TRAINING_REPORT_PATH)
    log.info(f"Training report saved: {TRAINING_REPORT_PATH}")

    # Build a Firestore-safe copy (no nested arrays)
    firestore_report = {k: v for k, v in report.items() if k != "confusion_matrix"}
    firestore_report["confusion_matrix"] = cm_str

    firestore_service.write_document(
        settings.COLLECTION_MODEL_RUNS,
        run_id,
        firestore_report,
        fallback_path=TRAINING_REPORT_PATH,
    )

    return report


def _train_random_forest(X_train, y_train) -> RandomForestClassifier:
    log.info("Training RandomForestClassifier …")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=settings.RANDOM_SEED,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    return model


def load_model():
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run 07_train_model.py first."
        )
    return joblib.load(MODEL_PATH)


def load_feature_columns() -> List[str]:
    if not os.path.isfile(FEATURE_COLS_PATH):
        raise FileNotFoundError(
            f"Feature columns file not found at {FEATURE_COLS_PATH}. Run 07_train_model.py first."
        )
    with open(FEATURE_COLS_PATH) as f:
        return json.load(f)
