"""
app/analysis/data_import.py
────────────────────────────
CSV data import utility for the official Track 2 datasets.

Expected files (place in data/ directory):
  - data/bhopal_ghats_2023_2025.csv
  - data/cpcb_water_quality_criteria.csv
  - data/sample_bhopal_2025.csv

Column mapping is documented below. If files are missing, import is skipped
and the function returns an ImportResult with a clear message.

IMPORTANT: This module only imports data from official CSV files.
It does NOT fabricate readings or claim sample data is official.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


@dataclass
class ImportResult:
    success: bool
    rows_imported: int = 0
    rows_skipped: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ── Column maps ───────────────────────────────────────────────────────────────
# Map CSV column name → model field name.
# Adjust if the official dataset uses different column names.

GHATS_CSV_COLUMN_MAP = {
    "ghat_name":            "name",
    "ghat_name_hi":         "name_hi",
    "location":             "location_description",
    "latitude":             "latitude",
    "longitude":            "longitude",
    "date":                 "sampling_date",
    "dissolved_oxygen_mgl": "dissolved_oxygen",
    "do_mgl":               "dissolved_oxygen",
    "bod_mgl":              "bod",
    "ph":                   "ph",
    "fecal_coliform":       "fecal_coliform",
    "total_coliform":       "total_coliform",
    "nitrate_mgl":          "nitrate",
    "turbidity_ntu":        "turbidity",
    "conductivity":         "conductivity",
    "temperature_c":        "temperature",
}

CPCB_CSV_COLUMN_MAP = {
    "parameter": "parameter",
    "water_class": "water_class",
    "min_value": "min_value",
    "max_value": "max_value",
    "unit": "unit",
    "description": "description",
}


def _parse_float(value: str) -> Optional[float]:
    try:
        v = value.strip()
        if v in ("", "N/A", "NA", "ND", "-"):
            return None
        return float(v)
    except ValueError:
        return None


def _parse_date(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def load_readings_from_csv(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse a readings CSV file into a list of dicts suitable for DB insert.
    Returns empty list if file not found.
    """
    if not filepath.exists():
        logger.warning("Dataset file not found", path=str(filepath))
        return []

    records: List[Dict[str, Any]] = []
    with filepath.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record: Dict[str, Any] = {}
            for csv_col, value in row.items():
                mapped = GHATS_CSV_COLUMN_MAP.get(csv_col.lower().strip())
                if mapped == "sampling_date":
                    record[mapped] = _parse_date(value)
                elif mapped in (
                    "dissolved_oxygen", "bod", "ph", "fecal_coliform",
                    "total_coliform", "nitrate", "turbidity", "conductivity",
                    "temperature", "latitude", "longitude",
                ):
                    record[mapped] = _parse_float(value)
                elif mapped:
                    record[mapped] = value.strip() or None
            if record:
                records.append(record)
    return records


def load_cpcb_thresholds_from_csv(filepath: Path) -> List[Dict[str, Any]]:
    """Parse the CPCB criteria CSV."""
    if not filepath.exists():
        return []
    records = []
    with filepath.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record: Dict[str, Any] = {}
            for csv_col, value in row.items():
                mapped = CPCB_CSV_COLUMN_MAP.get(csv_col.lower().strip())
                if mapped in ("min_value", "max_value"):
                    record[mapped] = _parse_float(value)
                elif mapped:
                    record[mapped] = value.strip() or None
            if record.get("parameter"):
                records.append(record)
    return records


def check_available_datasets() -> Dict[str, bool]:
    """Return which official datasets are available in the data/ directory."""
    files = {
        "bhopal_ghats_2023_2025.csv": (DATA_DIR / "bhopal_ghats_2023_2025.csv").exists(),
        "cpcb_water_quality_criteria.csv": (DATA_DIR / "cpcb_water_quality_criteria.csv").exists(),
        "sample_bhopal_2025.csv": (DATA_DIR / "sample_bhopal_2025.csv").exists(),
    }
    return files
