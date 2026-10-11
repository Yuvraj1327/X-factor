"""
app/api/v1/auth.py
───────────────────
Admin authentication endpoints.
No public registration — admins are created via setup script only.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.security import create_access_token, verify_password
from app.database.session import get_db
from app.models.admin import AdminUser
from app.repositories.admin_repo import AdminRepository
from app.schemas.auth import AdminOut, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Admin login")
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a BMC admin and return a JWT access token.
    Intentionally vague error to prevent user enumeration.
    """
    repo = AdminRepository(db)
    admin = await repo.get_by_email(data.email)

    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Update last_login
    admin.last_login = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token(subject=str(admin.id), extra_claims={"role": admin.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminOut, summary="Current admin profile")
async def me(admin: AdminUser = Depends(get_current_admin)):
    return admin
