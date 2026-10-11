"""
app/api/v1/ghats.py
────────────────────
Public ghat and reading endpoints (read-only, no auth required).
All responses include data disclaimers.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.engine import build_ghat_history
from app.database.session import get_db
from app.repositories.ghat_repo import GhatRepository
from app.schemas.analysis import GhatHistory
from app.schemas.ghat import CPCBThresholdOut, DataSourceOut, GhatDetail, GhatOut

router = APIRouter(prefix="/ghats", tags=["Ghats"])


@router.get("", response_model=List[GhatOut], summary="List all active ghats")
async def list_ghats(db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    return await repo.list_ghats()


@router.get("/{ghat_id}", response_model=GhatDetail, summary="Ghat details and latest readings")
async def get_ghat(ghat_id: int, db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    ghat = await repo.get_ghat(ghat_id)
    if not ghat:
        raise HTTPException(status_code=404, detail=f"Ghat {ghat_id} not found")
    readings = await repo.get_readings(ghat_id, limit=5)
    count = await repo.count_readings(ghat_id)
    return GhatDetail(
        **GhatOut.model_validate(ghat).model_dump(),
        latest_readings=readings,
        total_readings=count,
    )


@router.get("/{ghat_id}/history", response_model=GhatHistory, summary="Historical trend data")
async def ghat_history(
    ghat_id: int,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = GhatRepository(db)
    ghat = await repo.get_ghat(ghat_id)
    if not ghat:
        raise HTTPException(status_code=404, detail=f"Ghat {ghat_id} not found")
    readings = await repo.get_readings(ghat_id, limit=limit)
    reading_dicts = [
        {
            "sampling_date": r.sampling_date,
            "dissolved_oxygen": r.dissolved_oxygen,
            "bod": r.bod,
            "ph": r.ph,
            "fecal_coliform": r.fecal_coliform,
            "total_coliform": r.total_coliform,
            "source_id": r.source_id,
            "is_verified": r.is_verified,
        }
        for r in readings
    ]
    return build_ghat_history(ghat_id, ghat.name, reading_dicts)


@router.get("/sources", response_model=List[DataSourceOut], summary="Official data sources", tags=["Ghats"])
async def list_sources(db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    return await repo.list_sources()


@router.get("/thresholds", response_model=List[CPCBThresholdOut], summary="CPCB comparison thresholds", tags=["Ghats"])
async def list_thresholds(db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    return await repo.list_thresholds()
