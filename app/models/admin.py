"""
app/models/admin.py
────────────────────
Admin users and role model.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    BMC_OFFICER = "bmc_officer"
    DATA_ANALYST = "data_analyst"


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole), default=AdminRole.BMC_OFFICER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    advisories_created: Mapped[List["Advisory"]] = relationship(
        "Advisory", back_populates="created_by", foreign_keys="Advisory.created_by_id"
    )
    advisories_approved: Mapped[List["Advisory"]] = relationship(
        "Advisory", back_populates="approved_by", foreign_keys="Advisory.approved_by_id"
    )

    def __repr__(self) -> str:
        return f"<AdminUser id={self.id} email={self.email!r} role={self.role}>"
