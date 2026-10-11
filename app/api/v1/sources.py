"""
app/api/v1/sources.py
──────────────────────
Source reports and references endpoint.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.ghat_repo import GhatRepository
from app.schemas.ghat import DataSourceOut

router = APIRouter(prefix="/sources", tags=["Data Sources"])


@router.get("", response_model=List[DataSourceOut], summary="Official data sources and references")
async def list_sources(db: AsyncSession = Depends(get_db)):
    repo = GhatRepository(db)
    return await repo.list_sources()
