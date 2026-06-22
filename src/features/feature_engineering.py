"""
FR3 — Core Feature Engineering.
All features are computed using only historical matches BEFORE the current match date
to prevent data leakage.
"""
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from src.config import settings
from src.utils.file_utils import save_json, ensure_dir
from src.utils.logger import get_logger

log = get_logger(__name__)

FEATURES_CSV = os.path.join(settings.DATA_PROCESSED_DIR, "matches_features.csv")
FEATURE_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "feature_engineering_report.json")

WINDOW = settings.ROLLING_WINDOW

FEATURE_COLS: List[str] = [
    "home_form",
    "away_form",
    "home_goals_scored_avg",
    "home_goals_conceded_avg",
    "away_goals_scored_avg",
    "away_goals_conceded_avg",
    "h2h_home_wins",
    "h2h_draws",
    "h2h_away_wins",
    "home_advantage",
    "neutral_venue",
    "home_elo",
    "away_elo",
    "elo_diff",
]


class _TeamStats:
    """Rolling stats for a single team maintained chronologically."""

    def __init__(self):
        self.results: List[float] = []        # 1=win, 0.5=draw, 0=loss
        self.goals_scored: List[int] = []
        self.goals_conceded: List[int] = []
        self.elo: float = 1500.0

    def form(self) -> float:
        recent = self.results[-WINDOW:]
        return float(np.mean(recent)) if recent else 0.5

    def avg_scored(self) -> float:
        recent = self.goals_scored[-WINDOW:]
        return float(np.mean(recent)) if recent else 0.0

    def avg_conceded(self) -> float:
        recent = self.goals_conceded[-WINDOW:]
        return float(np.mean(recent)) if recent else 0.0

    def update(self, scored: int, conceded: int, is_win: bool, is_draw: bool, elo_change: float) -> None:
        result = 1.0 if is_win else (0.5 if is_draw else 0.0)
        self.results.append(result)
        self.goals_scored.append(scored)
        self.goals_conceded.append(conceded)
        self.elo += elo_change


class _H2HRecord:
    def __init__(self):
        self.home_wins = 0
        self.draws = 0
        self.away_wins = 0

    def update(self, outcome: str) -> None:
        if outcome == "home_win":
            self.home_wins += 1
        elif outcome == "draw":
            self.draws += 1
        else:
            self.away_wins += 1


def _elo_change(rating_a: float, rating_b: float, score_a: float, k: float = 32.0) -> float:
    expected_a = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
    return k * (score_a - expected_a)


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Starting feature engineering (leak-free, chronological).")

    df = df.copy().sort_values("date").reset_index(drop=True)

    team_stats: Dict[str, _TeamStats] = defaultdict(_TeamStats)
    h2h: Dict[tuple, _H2HRecord] = defaultdict(_H2HRecord)

    rows = []

    for _, row in df.iterrows():
        ht = row["home_team"]
        at = row["away_team"]
        pair = (min(ht, at), max(ht, at))

        hs = team_stats[ht]
        as_ = team_stats[at]
        h2h_rec = h2h[pair]

        feature_row = {
            "date": row["date"],
            "home_team": ht,
            "away_team": at,
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "outcome": row["outcome"],
            "tournament": row.get("tournament", "Unknown"),
            "neutral": bool(row.get("neutral", False)),
            # features from historical data (before this match)
            "home_form": hs.form(),
            "away_form": as_.form(),
            "home_goals_scored_avg": hs.avg_scored(),
            "home_goals_conceded_avg": hs.avg_conceded(),
            "away_goals_scored_avg": as_.avg_scored(),
            "away_goals_conceded_avg": as_.avg_conceded(),
            "h2h_home_wins": h2h_rec.home_wins,
            "h2h_draws": h2h_rec.draws,
            "h2h_away_wins": h2h_rec.away_wins,
            "home_advantage": int(not bool(row.get("neutral", False))),
            "neutral_venue": int(bool(row.get("neutral", False))),
            "home_elo": hs.elo,
            "away_elo": as_.elo,
            "elo_diff": hs.elo - as_.elo,
        }
        rows.append(feature_row)

        # Now update stats with the result of this match
        outcome = row["outcome"]
        home_score_a = 1.0 if outcome == "home_win" else (0.5 if outcome == "draw" else 0.0)
        away_score_a = 1.0 - home_score_a

        home_elo_delta = _elo_change(hs.elo, as_.elo, home_score_a)
        away_elo_delta = _elo_change(as_.elo, hs.elo, away_score_a)

        hs.update(
            scored=int(row["home_score"]),
            conceded=int(row["away_score"]),
            is_win=(outcome == "home_win"),
            is_draw=(outcome == "draw"),
            elo_change=home_elo_delta,
        )
        as_.update(
            scored=int(row["away_score"]),
            conceded=int(row["home_score"]),
            is_win=(outcome == "away_win"),
            is_draw=(outcome == "draw"),
            elo_change=away_elo_delta,
        )
        h2h_rec.update(outcome)

    features_df = pd.DataFrame(rows)
    log.info(f"Feature engineering complete — shape: {features_df.shape}")
    log.info(f"Feature columns: {FEATURE_COLS}")

    ensure_dir(settings.DATA_PROCESSED_DIR)
    features_df.to_csv(FEATURES_CSV, index=False)
    log.info(f"Features saved: {FEATURES_CSV}")

    report = {
        "input_rows": len(df),
        "output_rows": len(features_df),
        "feature_columns": FEATURE_COLS,
        "rolling_window": WINDOW,
        "output_file": FEATURES_CSV,
        "generated_at": datetime.utcnow().isoformat(),
    }
    save_json(report, FEATURE_REPORT_PATH)

    return features_df


def load_features_csv() -> pd.DataFrame:
    if not os.path.isfile(FEATURES_CSV):
        raise FileNotFoundError(
            f"Features CSV not found at {FEATURES_CSV}. Run 06_generate_features.py first."
        )
    df = pd.read_csv(FEATURES_CSV, parse_dates=["date"])
    log.info(f"Features CSV loaded — shape: {df.shape}")
    return df
