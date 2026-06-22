"""
Rule-based natural language explanation generator.
Translates feature importances into human-readable text.
No betting language. No fake claims.
"""
from typing import Dict, Any, List


def generate_explanation_text(
    home_team: str,
    away_team: str,
    prediction: str,
    top_features: List[Dict[str, Any]],
    confidence_tier: str,
    probabilities: Dict[str, float],
) -> str:
    pred_label = prediction.replace("_", " ").title()
    leading_prob = max(probabilities.values())

    # Build feature insight lines
    insights = []
    for feat in top_features[:4]:
        name = feat.get("display_name", feat["feature"])
        val = feat.get("feature_value", 0)
        direction = feat.get("direction", "")

        if feat["feature"] == "elo_diff":
            if val > 50:
                insights.append(f"a meaningful Elo rating advantage for {home_team} (Elo diff: {val:.0f})")
            elif val < -50:
                insights.append(f"a meaningful Elo rating advantage for {away_team} (Elo diff: {val:.0f})")
            else:
                insights.append("closely matched Elo ratings between both teams")
        elif feat["feature"] == "home_form":
            if val > 0.6:
                insights.append(f"strong recent form for {home_team}")
            elif val < 0.4:
                insights.append(f"below-average recent form for {home_team}")
        elif feat["feature"] == "away_form":
            if val > 0.6:
                insights.append(f"strong recent form for {away_team}")
            elif val < 0.4:
                insights.append(f"below-average recent form for {away_team}")
        elif feat["feature"] == "h2h_home_wins":
            if val > 3:
                insights.append(f"a favourable head-to-head record for {home_team}")
        elif feat["feature"] == "h2h_away_wins":
            if val > 3:
                insights.append(f"a favourable head-to-head record for {away_team}")
        elif feat["feature"] == "home_advantage":
            if val == 1:
                insights.append(f"{home_team} playing on home ground")
        elif feat["feature"] == "neutral_venue":
            if val == 1:
                insights.append("this match being played at a neutral venue")

    if not insights:
        insights = ["the overall historical statistics between these teams"]

    insight_str = ", ".join(insights[:3])
    confidence_note = _confidence_note(confidence_tier, leading_prob)

    lines = [
        f"The model predicts a {pred_label} based primarily on {insight_str}.",
        confidence_note,
        "This prediction is based on historical statistics and should be treated as an analytical estimate, not a certainty.",
    ]

    return " ".join(lines)


def _confidence_note(tier: str, leading_prob: float) -> str:
    if tier == "HIGH":
        return f"The model shows high confidence in this outcome (leading probability: {leading_prob:.1%})."
    elif tier == "MEDIUM":
        return f"The model shows moderate confidence (leading probability: {leading_prob:.1%}). There is meaningful uncertainty in this prediction."
    elif tier == "LOW":
        return f"Confidence is low (leading probability: {leading_prob:.1%}). The outcome probabilities are close — no single result dominates strongly."
    else:
        return "Model confidence is very low. The probability distribution is nearly uniform, indicating insufficient historical signal for this specific matchup."
