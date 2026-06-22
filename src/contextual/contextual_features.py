"""
FR13 — Contextual Intelligence Module.
Uses only fields available in the current dataset.
Unavailable signals are clearly marked — never faked.
"""
from datetime import datetime
from typing import Dict, Any, Optional

TOURNAMENT_TYPES = {
    "FIFA World Cup": "world_cup",
    "UEFA Euro": "continental_championship",
    "Copa America": "continental_championship",
    "Africa Cup of Nations": "continental_championship",
    "Asian Cup": "continental_championship",
    "FIFA World Cup qualification": "qualification",
    "UEFA Euro qualification": "qualification",
    "Friendly": "friendly",
    "Olympic Games": "major_tournament",
    "FIFA Confederations Cup": "major_tournament",
}

KNOWN_RIVALRIES = {
    frozenset({"Brazil", "Argentina"}),
    frozenset({"England", "Germany"}),
    frozenset({"England", "Argentina"}),
    frozenset({"Spain", "Portugal"}),
    frozenset({"France", "Germany"}),
    frozenset({"Netherlands", "Germany"}),
    frozenset({"India", "Pakistan"}),
    frozenset({"USA", "Mexico"}),
    frozenset({"Egypt", "Nigeria"}),
    frozenset({"South Korea", "Japan"}),
}


def classify_tournament(tournament: str) -> str:
    for key, t_type in TOURNAMENT_TYPES.items():
        if key.lower() in tournament.lower():
            return t_type
    return "other_competitive"


def is_rivalry(home_team: str, away_team: str) -> Optional[bool]:
    pair = frozenset({home_team, away_team})
    if pair in KNOWN_RIVALRIES:
        return True
    return None


def assess_neutrality(neutral: bool) -> str:
    return "neutral_venue" if neutral else "home_ground"


def get_season_context(date_str: str) -> Dict[str, Any]:
    try:
        dt = datetime.fromisoformat(str(date_str))
        month = dt.month
        season = "peak_season" if 6 <= month <= 8 else ("off_season" if month in (1, 2) else "regular_season")
        return {"month": month, "season_type": season}
    except Exception:
        return {"month": None, "season_type": "unknown"}


def build_context(
    home_team: str,
    away_team: str,
    tournament: str,
    neutral: bool,
    match_date: str,
    country: Optional[str] = None,
    city: Optional[str] = None,
) -> Dict[str, Any]:
    t_type = classify_tournament(tournament)
    rivalry = is_rivalry(home_team, away_team)
    venue_type = assess_neutrality(neutral)
    season_ctx = get_season_context(match_date)

    available = {
        "tournament": tournament,
        "tournament_type": t_type,
        "venue_type": venue_type,
        "neutral_venue": neutral,
        "season_context": season_ctx,
    }
    if rivalry is not None:
        available["rivalry_match"] = rivalry
    if country:
        available["host_country"] = country
    if city:
        available["host_city"] = city

    unavailable = {
        "weather": {
            "value": None,
            "status": "requires_external_api_or_location_coordinates",
            "note": "Planned Phase 03 integration via weather API + venue coordinates.",
        },
        "referee_tendency": {
            "value": None,
            "status": "not_available_in_dataset",
            "note": "Referee data is not present in the Kaggle international results dataset.",
        },
        "injury_suspension_impact": {
            "value": None,
            "status": "requires_external_injury_feed",
            "note": "Planned Phase 03 integration via official squad announcement feed.",
        },
        "crowd_attendance": {
            "value": None,
            "status": "not_available_in_dataset",
            "note": "Attendance data is not included in the current dataset.",
        },
        "transfer_window_recency": {
            "value": None,
            "status": "requires_squad_data",
            "note": "Transfer impact analysis requires squad composition data.",
        },
    }

    if rivalry is None:
        unavailable["rivalry_detection"] = {
            "value": None,
            "status": "not_reliably_inferable",
            "note": "Rivalry detection for this pair is uncertain. Only well-known rivalries are flagged.",
        }

    return {
        "match": f"{home_team} vs {away_team}",
        "home_team": home_team,
        "away_team": away_team,
        "match_date": match_date,
        "available_context": available,
        "unavailable_context": unavailable,
        "context_coverage_pct": round(
            len(available) / (len(available) + len(unavailable)) * 100, 1
        ),
    }
