"""
app/repositories/advisory_repo.py
───────────────────────────────────
Advisory database access.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.advisory import Advisory, AdvisoryStatus
from app.models.whatsapp import MessageStatus, WhatsAppMessage


class AdvisoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, advisory_id: int) -> Optional[Advisory]:
        return await self.db.get(Advisory, advisory_id)

    async def list_all(
        self,
        status: Optional[AdvisoryStatus] = None,
        ghat_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Advisory]:
        q = select(Advisory)
        if status:
            q = q.where(Advisory.status == status)
        if ghat_id:
            q = q.where(Advisory.ghat_id == ghat_id)
        q = q.order_by(Advisory.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Advisory:
        advisory = Advisory(**kwargs)
        self.db.add(advisory)
        await self.db.flush()
        await self.db.refresh(advisory)
        return advisory

    async def update(self, advisory: Advisory, updates: dict) -> Advisory:
        for k, v in updates.items():
            setattr(advisory, k, v)
        await self.db.flush()
        await self.db.refresh(advisory)
        return advisory

    async def get_delivery_stats(self, advisory_id: int) -> dict:
        from sqlalchemy import func
        result = await self.db.execute(
            select(WhatsAppMessage.status, func.count().label("count"))
            .where(WhatsAppMessage.advisory_id == advisory_id)
            .group_by(WhatsAppMessage.status)
        )
        rows = result.all()
        stats = {r.status: r.count for r in rows}
        return stats
