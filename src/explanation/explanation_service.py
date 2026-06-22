"""
FR6 — Explanation Service.
Orchestrates SHAP / RF-importance / rule-based explanation pipeline.
LLM support is optional — requires OPENAI_API_KEY in .env.
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.config import settings
from src.database import firestore_service
from src.explanation.shap_explainer import (
    SHAP_AVAILABLE,
    get_shap_importances,
    get_rf_importances,
)
from src.explanation.rule_explainer import generate_explanation_text
from src.utils.file_utils import save_json
from src.utils.logger import get_logger

log = get_logger(__name__)

EXPLANATION_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "explanation_report.json")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ENABLE_LLM = os.getenv("ENABLE_LLM_EXPLANATIONS", "false").lower() == "true"


def generate_full_explanation(
    model,
    feature_cols: List[str],
    feature_values: Dict[str, float],
    prediction_result: Dict[str, Any],
    confidence_result: Dict[str, Any],
) -> Dict[str, Any]:

    home_team = prediction_result.get("home_team", "Home")
    away_team = prediction_result.get("away_team", "Away")
    prediction = prediction_result.get("prediction", "unknown")
    probs = prediction_result.get("probabilities", {})
    confidence_tier = confidence_result.get("confidence_tier", "LOW")

    # 1. Try SHAP first
    top_features = None
    method = "rf_feature_importance"

    if SHAP_AVAILABLE:
        top_features = get_shap_importances(model, feature_values, feature_cols, prediction)
        if top_features:
            method = "shap"

    # 2. Fall back to RF importances
    if top_features is None:
        top_features = get_rf_importances(model, feature_cols, feature_values, prediction)

    # 3. Generate natural language explanation
    explanation_text = generate_explanation_text(
        home_team=home_team,
        away_team=away_team,
        prediction=prediction,
        top_features=top_features,
        confidence_tier=confidence_tier,
        probabilities=probs,
    )

    # 4. Optional LLM enhancement
    llm_text = None
    if ENABLE_LLM and OPENAI_API_KEY:
        llm_text = _try_llm_explanation(home_team, away_team, prediction, top_features, probs, explanation_text)

    report = {
        "match": f"{home_team} vs {away_team}",
        "match_date": prediction_result.get("match_date"),
        "prediction": prediction,
        "probabilities": probs,
        "confidence_tier": confidence_tier,
        "method": method,
        "shap_available": SHAP_AVAILABLE,
        "top_features": top_features,
        "explanation_text": llm_text if llm_text else explanation_text,
        "rule_based_text": explanation_text,
        "llm_enhanced": llm_text is not None,
        "generated_at": datetime.utcnow().isoformat(),
    }

    save_json(report, EXPLANATION_REPORT_PATH)
    log.info(f"Explanation report saved: {EXPLANATION_REPORT_PATH} (method: {method})")

    firestore_service.write_document(
        "explanations",
        "latest",
        _firestore_safe(report),
        fallback_path=EXPLANATION_REPORT_PATH,
    )

    return report


def _firestore_safe(report: Dict) -> Dict:
    """Strip nested complex objects that Firestore can't store."""
    safe = {}
    for k, v in report.items():
        if k == "top_features" and isinstance(v, list):
            safe[k] = [
                {fk: fv for fk, fv in f.items() if not isinstance(fv, (list, dict))}
                for f in v
            ]
        elif isinstance(v, (str, int, float, bool)) or v is None:
            safe[k] = v
        elif isinstance(v, dict):
            safe[k] = {dk: dv for dk, dv in v.items() if isinstance(dv, (str, int, float, bool))}
        else:
            safe[k] = str(v)
    return safe


def _try_llm_explanation(
    home_team: str,
    away_team: str,
    prediction: str,
    top_features: List[Dict],
    probs: Dict,
    fallback_text: str,
) -> Optional[str]:
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        features_summary = "; ".join(
            f"{f['display_name']}={f['feature_value']}" for f in top_features[:5]
        )
        prompt = (
            f"You are a football analytics assistant. Provide a neutral, analytical explanation "
            f"for why the model predicts {prediction.replace('_',' ')} for {home_team} vs {away_team}. "
            f"Key features: {features_summary}. "
            f"Probabilities: home_win={probs.get('home_win',0):.1%}, "
            f"draw={probs.get('draw',0):.1%}, away_win={probs.get('away_win',0):.1%}. "
            f"Write 2-3 sentences. Do not mention betting or gambling."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        log.warning(f"LLM explanation failed: {exc}. Using rule-based text.")
        return None
