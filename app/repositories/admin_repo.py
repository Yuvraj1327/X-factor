"""
app/repositories/admin_repo.py
───────────────────────────────
Admin user database access.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AdminUser


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[AdminUser]:
        result = await self.db.execute(
            select(AdminUser).where(AdminUser.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, admin_id: int) -> Optional[AdminUser]:
        return await self.db.get(AdminUser, admin_id)

    async def create(self, **kwargs) -> AdminUser:
        admin = AdminUser(**kwargs)
        self.db.add(admin)
        await self.db.flush()
        return admin

    async def count(self) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(AdminUser)
        )
        return result.scalar_one()
