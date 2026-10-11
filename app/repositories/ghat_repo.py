"""
app/repositories/ghat_repo.py
──────────────────────────────
Database access layer for ghats, readings, sources, and thresholds.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ghat import CPCBThreshold, DataSource, Ghat, WaterQualityReading


class GhatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_ghats(self, active_only: bool = True) -> List[Ghat]:
        q = select(Ghat)
        if active_only:
            q = q.where(Ghat.status == "active")
        result = await self.db.execute(q.order_by(Ghat.name))
        return list(result.scalars().all())

    async def get_ghat(self, ghat_id: int) -> Optional[Ghat]:
        return await self.db.get(Ghat, ghat_id)

    async def get_ghat_by_slug(self, slug: str) -> Optional[Ghat]:
        result = await self.db.execute(select(Ghat).where(Ghat.slug == slug))
        return result.scalar_one_or_none()

    async def get_latest_reading(self, ghat_id: int) -> Optional[WaterQualityReading]:
        result = await self.db.execute(
            select(WaterQualityReading)
            .where(WaterQualityReading.ghat_id == ghat_id)
            .options(selectinload(WaterQualityReading.source))
            .order_by(WaterQualityReading.sampling_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_readings(
        self, ghat_id: int, limit: int = 50, offset: int = 0
    ) -> List[WaterQualityReading]:
        result = await self.db.execute(
            select(WaterQualityReading)
            .where(WaterQualityReading.ghat_id == ghat_id)
            .options(selectinload(WaterQualityReading.source))
            .order_by(WaterQualityReading.sampling_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_all_readings(self) -> List[WaterQualityReading]:
        result = await self.db.execute(
            select(WaterQualityReading).order_by(WaterQualityReading.sampling_date.desc())
        )
        return list(result.scalars().all())

    async def create_reading(self, data: dict) -> WaterQualityReading:
        reading = WaterQualityReading(**data)
        self.db.add(reading)
        await self.db.flush()
        return reading

    async def count_readings(self, ghat_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(WaterQualityReading.ghat_id == ghat_id)
        )
        return result.scalar_one()

    async def list_sources(self) -> List[DataSource]:
        result = await self.db.execute(select(DataSource).order_by(DataSource.title))
        return list(result.scalars().all())

    async def list_thresholds(self) -> List[CPCBThreshold]:
        result = await self.db.execute(select(CPCBThreshold).order_by(CPCBThreshold.parameter))
        return list(result.scalars().all())

    async def get_thresholds_as_dict(self) -> Dict:
        """Return thresholds keyed by parameter name for the analysis engine."""
        from app.analysis.cpcb_rules import Threshold, get_default_thresholds
        db_thresholds = await self.list_thresholds()
        if not db_thresholds:
            return get_default_thresholds()
        return {
            t.parameter: Threshold(
                parameter=t.parameter,
                water_class=t.water_class,
                min_value=t.min_value,
                max_value=t.max_value,
                unit=t.unit,
                description=t.description or "",
            )
            for t in db_thresholds
        }

    async def upsert_ghat(self, name: str, slug: str, **kwargs) -> Ghat:
        result = await self.db.execute(select(Ghat).where(Ghat.slug == slug))
        ghat = result.scalar_one_or_none()
        if not ghat:
            ghat = Ghat(name=name, slug=slug, **kwargs)
            self.db.add(ghat)
            await self.db.flush()
        return ghat

    async def upsert_threshold(self, parameter: str, **kwargs) -> CPCBThreshold:
        result = await self.db.execute(
            select(CPCBThreshold).where(CPCBThreshold.parameter == parameter)
        )
        t = result.scalar_one_or_none()
        if not t:
            t = CPCBThreshold(parameter=parameter, **kwargs)
            self.db.add(t)
        else:
            for k, v in kwargs.items():
                setattr(t, k, v)
        await self.db.flush()
        return t
