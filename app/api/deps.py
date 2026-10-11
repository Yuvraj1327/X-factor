"""
app/api/deps.py
────────────────
FastAPI dependency functions for authentication and database access.
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.admin import AdminRole, AdminUser
from app.repositories.admin_repo import AdminRepository


async def get_current_admin(
    authorization: str = Header(..., description="Bearer <token>"),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not authorization.startswith("Bearer "):
        raise credentials_exception
    token = authorization[7:]
    try:
        payload = decode_access_token(token)
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = AdminRepository(db)
    admin = await repo.get_by_id(int(admin_id))
    if not admin or not admin.is_active:
        raise credentials_exception
    return admin


async def require_approver(
    admin: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    """Only BMC officers and super admins can approve advisories."""
    if admin.role not in (AdminRole.BMC_OFFICER, AdminRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only BMC Officers can perform this action",
        )
    return admin
