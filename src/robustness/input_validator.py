"""Input validation for prediction requests — FR18."""

import re
from datetime import datetime, date
from typing import Optional, Tuple

from pydantic import BaseModel, field_validator, model_validator

_DATE_MIN = date(1872, 1, 1)   # dataset starts 1872
_DATE_MAX_YEARS_AHEAD = 2      # reject dates > 2 years in future
_QUERY_MAX_LEN = 1000
_INJECTION_PATTERN = re.compile(r"[<>\"';]|--|/\*|\*/|xp_|UNION|SELECT|DROP|INSERT", re.IGNORECASE)


def sanitise_string(value: str) -> str:
    """Remove characters that could be used in injection attacks."""
    return _INJECTION_PATTERN.sub("", value).strip()


def validate_team_name(name: str) -> Tuple[bool, str]:
    name = name.strip()
    if not name:
        return False, "Team name cannot be empty."
    if len(name) > 100:
        return False, "Team name too long (max 100 chars)."
    if _INJECTION_PATTERN.search(name):
        return False, "Team name contains disallowed characters."
    return True, ""


def validate_match_date(date_str: str) -> Tuple[bool, str]:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."
    from datetime import timedelta
    max_future = date.today().replace(year=date.today().year + _DATE_MAX_YEARS_AHEAD)
    if d < _DATE_MIN:
        return False, f"Date cannot be before {_DATE_MIN}."
    if d > max_future:
        return False, f"Date cannot be more than {_DATE_MAX_YEARS_AHEAD} years in the future."
    return True, ""


class CustomPredictionRequest(BaseModel):
    home_team:     str
    away_team:     str
    match_date:    str
    tournament:    Optional[str] = "Friendly"
    neutral_venue: Optional[bool] = False

    @field_validator("home_team", "away_team")
    @classmethod
    def clean_team(cls, v):
        v = sanitise_string(v)
        ok, msg = validate_team_name(v)
        if not ok:
            raise ValueError(msg)
        return v

    @field_validator("match_date")
    @classmethod
    def check_date(cls, v):
        ok, msg = validate_match_date(v)
        if not ok:
            raise ValueError(msg)
        return v

    @field_validator("tournament")
    @classmethod
    def clean_tournament(cls, v):
        if v:
            return sanitise_string(v)[:200]
        return v

    @model_validator(mode="after")
    def teams_different(self):
        if self.home_team.lower() == self.away_team.lower():
            raise ValueError("Home team and away team must be different.")
        return self


class AgentQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty.")
        if len(v) > _QUERY_MAX_LEN:
            raise ValueError(f"Query too long (max {_QUERY_MAX_LEN} chars).")
        return v
