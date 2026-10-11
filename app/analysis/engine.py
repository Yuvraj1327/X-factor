"""
app/analysis/engine.py
───────────────────────
Water-quality analysis engine.

Design principles:
  - All rankings are data-based priority indicators, NOT safety certifications.
  - Missing parameters are flagged, never assumed safe.
  - Stale data is identified and labelled clearly.
  - Risk scores are deterministic and documented.
  - No AI-generated risk scores; all logic is explicit and auditable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.analysis.cpcb_rules import Threshold, get_default_thresholds
from app.core.config import get_settings
from app.schemas.analysis import (
    AnalysisSummary,
    GhatHistory,
    GhatRanking,
    HistoryPoint,
    ParameterStatus,
)

settings = get_settings()

_ASSESSED_PARAMS = [
    "dissolved_oxygen", "bod", "ph", "fecal_coliform", "total_coliform",
    "nitrate", "turbidity",
]

_DISCLAIMER = (
    "Rankings are based on available historical data only. "
    "They are data-priority indicators, NOT official safety certifications. "
    "Do not use these rankings as the sole basis for public safety decisions. "
    "Readings are labelled with their sampling date and source."
)


def _is_fresh(sampling_date: Optional[datetime]) -> bool:
    if sampling_date is None:
        return False
    now = datetime.now(timezone.utc)
    if sampling_date.tzinfo is None:
        sampling_date = sampling_date.replace(tzinfo=timezone.utc)
    delta = now - sampling_date
    return delta.days <= settings.DATA_FRESHNESS_THRESHOLD_DAYS


def _data_age_days(sampling_date: Optional[datetime]) -> Optional[int]:
    if sampling_date is None:
        return None
    now = datetime.now(timezone.utc)
    if sampling_date.tzinfo is None:
        sampling_date = sampling_date.replace(tzinfo=timezone.utc)
    return (now - sampling_date).days


def _assess_parameter(
    param: str,
    value: Optional[float],
    thresholds: Dict[str, Threshold],
) -> ParameterStatus:
    threshold = thresholds.get(param)
    missing = value is None
    exceeds: Optional[bool] = None
    if threshold and not missing:
        exceeds = threshold.exceeds(value)  # type: ignore[arg-type]

    return ParameterStatus(
        parameter=param,
        value=value,
        unit=threshold.unit if threshold else "",
        cpcb_min=threshold.min_value if threshold else None,
        cpcb_max=threshold.max_value if threshold else None,
        water_class=threshold.water_class if threshold else "B",
        exceeds_limit=exceeds,
        missing=missing,
    )


def _risk_score(evidence: List[ParameterStatus]) -> float:
    """
    Deterministic risk score 0–100.

    Scoring rules (all documented):
      - Each assessed parameter contributes up to 100/N points (N = total params).
      - Parameter EXCEEDS limit    → full contribution.
      - Parameter is MISSING       → 60 % of full contribution (precautionary).
      - Parameter is within limit  → 0 contribution.
    Missing data is never assumed safe; it contributes a precautionary penalty.
    """
    n = len(evidence)
    if n == 0:
        return 0.0
    per_param = 100.0 / n
    score = 0.0
    for e in evidence:
        if e.missing:
            score += per_param * 0.6
        elif e.exceeds_limit:
            score += per_param
    return round(min(score, 100.0), 2)


def _risk_label(score: float, has_any_data: bool) -> str:
    if not has_any_data:
        return "INSUFFICIENT_DATA"
    if score >= 60:
        return "HIGH_PRIORITY"
    if score >= 30:
        return "MODERATE_PRIORITY"
    return "LOW_PRIORITY"


def rank_ghats(
    ghats_data: List[Dict],
    thresholds: Optional[Dict[str, Threshold]] = None,
) -> List[GhatRanking]:
    """
    Rank ghats by risk priority.

    `ghats_data` is a list of dicts with keys:
        ghat_id, ghat_name, ghat_slug, latest_reading (dict or None)

    Returns a sorted list, rank 1 = highest priority concern.
    """
    if thresholds is None:
        thresholds = get_default_thresholds()

    rankings: List[GhatRanking] = []

    for gd in ghats_data:
        reading = gd.get("latest_reading")
        sampling_date: Optional[datetime] = None
        evidence: List[ParameterStatus] = []

        if reading:
            sampling_date = reading.get("sampling_date")
            for param in _ASSESSED_PARAMS:
                evidence.append(
                    _assess_parameter(param, reading.get(param), thresholds)
                )

        has_data = bool(reading)
        score = _risk_score(evidence) if has_data else 50.0  # unknown = moderate concern
        label = _risk_label(score, has_data)

        rankings.append(
            GhatRanking(
                ghat_id=gd["ghat_id"],
                ghat_name=gd["ghat_name"],
                ghat_slug=gd["ghat_slug"],
                priority_rank=0,  # filled below
                risk_score=score,
                risk_label=label,
                parameters_assessed=len(evidence),
                parameters_exceeding=sum(1 for e in evidence if e.exceeds_limit),
                parameters_missing=sum(1 for e in evidence if e.missing),
                latest_sampling_date=sampling_date,
                data_age_days=_data_age_days(sampling_date),
                is_data_fresh=_is_fresh(sampling_date),
                data_disclaimer=_DISCLAIMER,
                evidence=evidence,
            )
        )

    # Sort: highest score first; ties: ghats with data before those without
    rankings.sort(key=lambda r: (-r.risk_score, r.ghat_name))
    for i, r in enumerate(rankings, start=1):
        r.priority_rank = i

    return rankings


def build_summary(
    ghats_data: List[Dict],
    all_readings: List[Dict],
) -> AnalysisSummary:
    ghats_with_data = sum(1 for g in ghats_data if g.get("latest_reading"))
    ghats_without = len(ghats_data) - ghats_with_data
    fresh_count = sum(
        1 for g in ghats_data
        if g.get("latest_reading") and _is_fresh(g["latest_reading"].get("sampling_date"))
    )

    dates = [
        r["sampling_date"] for r in all_readings if r.get("sampling_date")
    ]
    params_available = sorted(set(
        p for r in all_readings for p in _ASSESSED_PARAMS if r.get(p) is not None
    ))

    return AnalysisSummary(
        total_ghats=len(ghats_data),
        ghats_with_data=ghats_with_data,
        ghats_without_data=ghats_without,
        ghats_with_fresh_data=fresh_count,
        total_readings=len(all_readings),
        date_range_start=min(dates) if dates else None,
        date_range_end=max(dates) if dates else None,
        parameters_available=params_available,
        data_disclaimer=_DISCLAIMER,
        generated_at=datetime.now(timezone.utc),
    )


def build_ghat_history(
    ghat_id: int,
    ghat_name: str,
    readings: List[Dict],
) -> GhatHistory:
    points = [
        HistoryPoint(
            sampling_date=r["sampling_date"],
            dissolved_oxygen=r.get("dissolved_oxygen"),
            bod=r.get("bod"),
            ph=r.get("ph"),
            fecal_coliform=r.get("fecal_coliform"),
            total_coliform=r.get("total_coliform"),
            source_id=r.get("source_id"),
            is_verified=r.get("is_verified", False),
        )
        for r in sorted(readings, key=lambda x: x["sampling_date"])
    ]
    return GhatHistory(
        ghat_id=ghat_id,
        ghat_name=ghat_name,
        readings=points,
        total_count=len(points),
    )
