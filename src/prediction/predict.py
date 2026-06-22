"""
FR4 — Basic Prediction Engine.
Generates a match outcome prediction using the trained model and historical data.
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

import numpy as np
import pandas as pd

from src.config import settings
from src.database import firestore_service
from src.features.feature_engineering import _TeamStats, _H2HRecord, _elo_change, WINDOW
from src.training.train_model import load_model, load_feature_columns
from src.utils.file_utils import save_json, ensure_dir
from src.utils.logger import get_logger

log = get_logger(__name__)

SAMPLE_PREDICTION_PATH = os.path.join(settings.DATA_REPORTS_DIR, "sample_prediction.json")

LABEL_MAP = {0: "home_win", 1: "draw", 2: "away_win"}


def predict_match(
    home_team: str,
    away_team: str,
    match_date: str,
    historical_df: pd.DataFrame,
    tournament: str = "Friendly",
    neutral: bool = False,
) -> Dict[str, Any]:

    model = load_model()
    feature_cols = load_feature_columns()

    features = _build_features(
        home_team=home_team,
        away_team=away_team,
        match_date=pd.Timestamp(match_date),
        historical_df=historical_df,
        neutral=neutral,
    )

    X = np.array([[features[col] for col in feature_cols]])
    proba = model.predict_proba(X)[0]

    classes = model.classes_
    proba_dict = {LABEL_MAP[c]: float(round(p, 4)) for c, p in zip(classes, proba)}

    predicted_class_idx = int(np.argmax(proba))
    prediction = LABEL_MAP[classes[predicted_class_idx]]
    confidence = float(round(max(proba), 4))

    result: Dict[str, Any] = {
        "home_team": home_team,
        "away_team": away_team,
        "match_date": match_date,
        "tournament": tournament,
        "neutral_venue": neutral,
        "prediction": prediction,
        "probabilities": proba_dict,
        "confidence": confidence,
        "predicted_at": datetime.utcnow().isoformat(),
    }

    log.info(f"Prediction: {home_team} vs {away_team} -> {prediction} (confidence: {confidence:.2%})")
    log.info(f"Probabilities: {proba_dict}")

    return result


def _build_features(
    home_team: str,
    away_team: str,
    match_date: pd.Timestamp,
    historical_df: pd.DataFrame,
    neutral: bool,
) -> Dict[str, float]:

    past = historical_df[historical_df["date"] < match_date].copy()

    ht_stats = _TeamStats()
    at_stats = _TeamStats()

    for _, row in past.sort_values("date").iterrows():
        involved_home = row["home_team"] == home_team
        involved_away = row["home_team"] == away_team
        involved_as_away_home = row["away_team"] == home_team
        involved_as_away_away = row["away_team"] == away_team

        outcome = row["outcome"]

        if involved_home:
            home_score_a = 1.0 if outcome == "home_win" else (0.5 if outcome == "draw" else 0.0)
            delta = _elo_change(ht_stats.elo, 1500.0, home_score_a)
            ht_stats.update(
                scored=int(row["home_score"]),
                conceded=int(row["away_score"]),
                is_win=(outcome == "home_win"),
                is_draw=(outcome == "draw"),
                elo_change=delta,
            )
        elif involved_as_away_home:
            away_score_a = 1.0 if outcome == "away_win" else (0.5 if outcome == "draw" else 0.0)
            delta = _elo_change(ht_stats.elo, 1500.0, away_score_a)
            ht_stats.update(
                scored=int(row["away_score"]),
                conceded=int(row["home_score"]),
                is_win=(outcome == "away_win"),
                is_draw=(outcome == "draw"),
                elo_change=delta,
            )

        if involved_away:
            home_score_a2 = 1.0 if outcome == "home_win" else (0.5 if outcome == "draw" else 0.0)
            delta = _elo_change(at_stats.elo, 1500.0, home_score_a2)
            at_stats.update(
                scored=int(row["home_score"]),
                conceded=int(row["away_score"]),
                is_win=(outcome == "home_win"),
                is_draw=(outcome == "draw"),
                elo_change=delta,
            )
        elif involved_as_away_away:
            away_score_a2 = 1.0 if outcome == "away_win" else (0.5 if outcome == "draw" else 0.0)
            delta = _elo_change(at_stats.elo, 1500.0, away_score_a2)
            at_stats.update(
                scored=int(row["away_score"]),
                conceded=int(row["home_score"]),
                is_win=(outcome == "away_win"),
                is_draw=(outcome == "draw"),
                elo_change=delta,
            )

    # H2H
    pair = (min(home_team, away_team), max(home_team, away_team))
    h2h_rec = _H2HRecord()
    h2h_past = past[
        ((past["home_team"] == home_team) & (past["away_team"] == away_team)) |
        ((past["home_team"] == away_team) & (past["away_team"] == home_team))
    ]
    for _, row in h2h_past.iterrows():
        if row["home_team"] == home_team:
            h2h_rec.update(row["outcome"])
        else:
            flipped = {"home_win": "away_win", "away_win": "home_win", "draw": "draw"}
            h2h_rec.update(flipped[row["outcome"]])

    return {
        "home_form": ht_stats.form(),
        "away_form": at_stats.form(),
        "home_goals_scored_avg": ht_stats.avg_scored(),
        "home_goals_conceded_avg": ht_stats.avg_conceded(),
        "away_goals_scored_avg": at_stats.avg_scored(),
        "away_goals_conceded_avg": at_stats.avg_conceded(),
        "h2h_home_wins": float(h2h_rec.home_wins),
        "h2h_draws": float(h2h_rec.draws),
        "h2h_away_wins": float(h2h_rec.away_wins),
        "home_advantage": float(not neutral),
        "neutral_venue": float(neutral),
        "home_elo": ht_stats.elo,
        "away_elo": at_stats.elo,
        "elo_diff": ht_stats.elo - at_stats.elo,
    }


def run_sample_prediction(historical_df: pd.DataFrame) -> Dict[str, Any]:
    result = predict_match(
        home_team="Brazil",
        away_team="Argentina",
        match_date="2017-06-01",
        historical_df=historical_df,
        tournament="FIFA World Cup qualification",
        neutral=False,
    )

    save_json(result, SAMPLE_PREDICTION_PATH)
    log.info(f"Sample prediction saved: {SAMPLE_PREDICTION_PATH}")

    firestore_service.write_document(
        settings.COLLECTION_PREDICTIONS,
        "sample_brazil_vs_argentina",
        result,
        fallback_path=SAMPLE_PREDICTION_PATH,
    )

    return result
