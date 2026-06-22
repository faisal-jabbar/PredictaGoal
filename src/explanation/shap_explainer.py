"""
SHAP-based feature importance explainer.
Falls back gracefully if SHAP is not installed or fails.
"""
from typing import Dict, Any, List, Optional
import numpy as np

from src.utils.logger import get_logger

log = get_logger(__name__)

SHAP_AVAILABLE = False
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    log.warning("SHAP not installed. Rule-based fallback will be used.")

FEATURE_DISPLAY_NAMES = {
    "home_form": "Home Team Form",
    "away_form": "Away Team Form",
    "home_goals_scored_avg": "Home Goals Scored (avg)",
    "home_goals_conceded_avg": "Home Goals Conceded (avg)",
    "away_goals_scored_avg": "Away Goals Scored (avg)",
    "away_goals_conceded_avg": "Away Goals Conceded (avg)",
    "h2h_home_wins": "H2H Home Wins",
    "h2h_draws": "H2H Draws",
    "h2h_away_wins": "H2H Away Wins",
    "home_advantage": "Home Advantage",
    "neutral_venue": "Neutral Venue",
    "home_elo": "Home Team Elo",
    "away_elo": "Away Team Elo",
    "elo_diff": "Elo Difference",
}


def get_shap_importances(
    model,
    feature_values: Dict[str, float],
    feature_cols: List[str],
    prediction: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Returns SHAP values for the given prediction, or None if SHAP unavailable.
    """
    if not SHAP_AVAILABLE:
        return None

    try:
        X = np.array([[feature_values[col] for col in feature_cols]])
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        label_map = {0: "home_win", 1: "draw", 2: "away_win"}
        pred_class_idx = [k for k, v in label_map.items() if v == prediction]
        if not pred_class_idx:
            return None
        class_idx = pred_class_idx[0]

        sv = shap_values[class_idx][0] if isinstance(shap_values, list) else shap_values[0]
        importances = []
        for col, val in zip(feature_cols, sv):
            importances.append({
                "feature": col,
                "shap_value": float(round(val, 4)),
                "feature_value": float(round(feature_values.get(col, 0), 4)),
                "display_name": FEATURE_DISPLAY_NAMES.get(col, col),
                "direction": "supports_home_win" if val > 0 else "against_home_win",
                "importance": float(round(abs(val), 4)),
            })

        importances.sort(key=lambda x: x["importance"], reverse=True)
        return importances[:8]

    except Exception as exc:
        log.warning(f"SHAP failed: {exc}. Falling back to feature importance.")
        return None


def get_rf_importances(
    model,
    feature_cols: List[str],
    feature_values: Dict[str, float],
    prediction: str,
) -> List[Dict[str, Any]]:
    """
    RandomForest built-in feature importances as fallback.
    Augmented with feature value direction logic.
    """
    importances_raw = model.feature_importances_
    results = []
    for col, imp in zip(feature_cols, importances_raw):
        val = feature_values.get(col, 0)
        direction = _infer_direction(col, val, prediction)
        results.append({
            "feature": col,
            "importance": float(round(imp, 4)),
            "feature_value": float(round(val, 4)),
            "display_name": FEATURE_DISPLAY_NAMES.get(col, col),
            "direction": direction,
            "shap_value": None,
        })

    results.sort(key=lambda x: x["importance"], reverse=True)
    return results[:8]


def _infer_direction(feature: str, value: float, prediction: str) -> str:
    home_positive = {"elo_diff", "home_form", "home_goals_scored_avg", "h2h_home_wins", "home_advantage", "home_elo"}
    away_positive = {"away_form", "away_goals_scored_avg", "h2h_away_wins", "away_elo"}

    if feature in home_positive:
        return "supports_home_win" if value > 0 else "neutral_or_against"
    if feature in away_positive:
        return "supports_away_win" if value > 0 else "neutral_or_against"
    return "contextual"
