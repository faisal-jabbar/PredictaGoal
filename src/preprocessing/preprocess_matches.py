"""
FR2 — Data Preprocessing Module.
Cleans raw match data and creates the outcome target variable.
"""
import os
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import numpy as np

from src.config import settings
from src.database import firestore_service
from src.utils.file_utils import save_json, ensure_dir
from src.utils.logger import get_logger

log = get_logger(__name__)

PROCESSED_CSV = os.path.join(settings.DATA_PROCESSED_DIR, "matches_processed.csv")
QUALITY_REPORT_PATH = os.path.join(settings.DATA_REPORTS_DIR, "data_quality_report.json")

REQUIRED_COLS = {"date", "home_team", "away_team", "home_score", "away_score"}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Starting preprocessing pipeline.")
    initial_rows = len(df)

    df = df.copy()
    _validate_required_columns(df)

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["date"])
    log.info(f"Dropped {before - len(df)} rows with invalid dates.")

    # Clean team names
    df["home_team"] = df["home_team"].str.strip()
    df["away_team"] = df["away_team"].str.strip()

    # Score validation — must be non-negative integers
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["home_score", "away_score"])
    df = df[(df["home_score"] >= 0) & (df["away_score"] >= 0)]
    log.info(f"Dropped {before - len(df)} rows with invalid scores.")

    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["date", "home_team", "away_team"])
    log.info(f"Dropped {before - len(df)} duplicate rows.")

    # Remove rows missing teams
    before = len(df)
    df = df.dropna(subset=["home_team", "away_team"])
    df = df[df["home_team"].str.len() > 0]
    df = df[df["away_team"].str.len() > 0]
    log.info(f"Dropped {before - len(df)} rows with empty team names.")

    # Create outcome label
    df["outcome"] = df.apply(_determine_outcome, axis=1)

    # Neutral venue flag
    if "neutral" in df.columns:
        df["neutral"] = df["neutral"].fillna(False).astype(bool)
    else:
        df["neutral"] = False

    # Fill optional text columns
    for col in ["tournament", "city", "country"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = "Unknown"

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    log.info(f"Preprocessing complete. {initial_rows} -> {len(df)} rows.")

    # Save
    ensure_dir(settings.DATA_PROCESSED_DIR)
    df.to_csv(PROCESSED_CSV, index=False)
    log.info(f"Processed data saved: {PROCESSED_CSV}")

    report = _build_quality_report(df, initial_rows)
    save_json(report, QUALITY_REPORT_PATH)
    log.info(f"Data quality report saved: {QUALITY_REPORT_PATH}")

    firestore_service.write_document(
        settings.COLLECTION_DATA_QUALITY,
        "latest",
        report,
        fallback_path=QUALITY_REPORT_PATH,
    )

    return df


def _validate_required_columns(df: pd.DataFrame) -> None:
    cols_lower = {c.strip().lower().replace(" ", "_") for c in df.columns}
    missing = REQUIRED_COLS - cols_lower
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")


def _determine_outcome(row) -> str:
    if row["home_score"] > row["away_score"]:
        return "home_win"
    elif row["home_score"] == row["away_score"]:
        return "draw"
    else:
        return "away_win"


def _build_quality_report(df: pd.DataFrame, initial_rows: int) -> Dict[str, Any]:
    date_range = (
        str(df["date"].min().date()) if not df.empty else "N/A",
        str(df["date"].max().date()) if not df.empty else "N/A",
    )
    outcome_dist = df["outcome"].value_counts().to_dict() if "outcome" in df.columns else {}

    return {
        "total_rows_loaded": initial_rows,
        "rows_removed": initial_rows - len(df),
        "final_usable_rows": len(df),
        "missing_value_summary": df.isnull().sum().to_dict(),
        "date_range": {"from": date_range[0], "to": date_range[1]},
        "unique_teams": int(
            pd.concat([df["home_team"], df["away_team"]]).nunique()
        ),
        "unique_tournaments": int(df["tournament"].nunique()) if "tournament" in df.columns else 0,
        "outcome_distribution": {k: int(v) for k, v in outcome_dist.items()},
        "output_file": PROCESSED_CSV,
        "generated_at": datetime.utcnow().isoformat(),
    }


def load_processed_csv() -> pd.DataFrame:
    if not os.path.isfile(PROCESSED_CSV):
        raise FileNotFoundError(
            f"Processed CSV not found at {PROCESSED_CSV}. Run 05_preprocess_data.py first."
        )
    df = pd.read_csv(PROCESSED_CSV, parse_dates=["date"])
    log.info(f"Processed CSV loaded — shape: {df.shape}")
    return df
