"""
app/api/v1/analysis.py
───────────────────────
Analysis and ranking endpoints — BMC admin dashboard data.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.engine import build_summary, rank_ghats
from app.database.session import get_db
from app.repositories.ghat_repo import GhatRepository
from app.schemas.analysis import AnalysisSummary, GhatRanking

router = APIRouter(prefix="/analysis", tags=["Analysis"])


async def _build_ghats_data(repo: GhatRepository):
    ghats = await repo.list_ghats()
    result = []
    for g in ghats:
        reading = await repo.get_latest_reading(g.id)
        reading_dict = None
        if reading:
            reading_dict = {
                "sampling_date": reading.sampling_date,
                "dissolved_oxygen": reading.dissolved_oxygen,
                "bod": reading.bod,
                "ph": reading.ph,
                "fecal_coliform": reading.fecal_coliform,
                "total_coliform": reading.total_coliform,
                "nitrate": reading.nitrate,
                "turbidity": reading.turbidity,
                "conductivity": reading.conductivity,
                "temperature": reading.temperature,
            }
        result.append({
            "ghat_id": g.id,
            "ghat_name": g.name,
            "ghat_slug": g.slug,
            "latest_reading": reading_dict,
        })
    return result


@router.get("/summary", response_model=AnalysisSummary, summary="Overall data summary")
async def analysis_summary(db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    ghats_data = await _build_ghats_data(repo)
    all_readings = await repo.get_all_readings()
    all_dicts = [
        {"sampling_date": r.sampling_date, **{
            p: getattr(r, p) for p in [
                "dissolved_oxygen", "bod", "ph", "fecal_coliform",
                "total_coliform", "nitrate", "turbidity",
            ]
        }}
        for r in all_readings
    ]
    return build_summary(ghats_data, all_dicts)


@router.get("/rankings", response_model=List[GhatRanking], summary="Evidence-based risk-priority rankings")
async def analysis_rankings(db: AsyncSession = Depends(get_db)):
    """
    Returns ghats ranked by data-based risk priority (highest concern first).
    NOT an official safety certification.
    """
    repo = GhatRepository(db)
    ghats_data = await _build_ghats_data(repo)
    thresholds = await repo.get_thresholds_as_dict()
    return rank_ghats(ghats_data, thresholds)
