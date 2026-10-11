"""
app/scripts/create_admin.py
────────────────────────────
Secure admin bootstrap script.

Usage:
    python -m app.scripts.create_admin

Reads BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD from environment.
Will NOT overwrite an existing admin with the same email.
Will NOT run if no password is set.
"""
from __future__ import annotations

import asyncio
import sys

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.database.session import AsyncSessionLocal
from app.models.admin import AdminRole, AdminUser
from app.repositories.admin_repo import AdminRepository

configure_logging()
logger = get_logger(__name__)


async def create_admin() -> None:
    settings = get_settings()

    if not settings.BOOTSTRAP_ADMIN_EMAIL:
        logger.error("BOOTSTRAP_ADMIN_EMAIL is not set. Aborting.")
        sys.exit(1)

    if not settings.BOOTSTRAP_ADMIN_PASSWORD or len(settings.BOOTSTRAP_ADMIN_PASSWORD) < 12:
        logger.error(
            "BOOTSTRAP_ADMIN_PASSWORD must be at least 12 characters. Aborting."
        )
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            repo = AdminRepository(session)
            existing = await repo.get_by_email(settings.BOOTSTRAP_ADMIN_EMAIL)
            if existing:
                logger.warning(
                    "Admin already exists — not overwriting",
                    email=settings.BOOTSTRAP_ADMIN_EMAIL,
                )
                return

            admin = await repo.create(
                email=settings.BOOTSTRAP_ADMIN_EMAIL.lower(),
                full_name="BMC Super Admin",
                hashed_password=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
            )
            logger.info(
                "Admin created successfully",
                email=settings.BOOTSTRAP_ADMIN_EMAIL,
                admin_id=admin.id,
            )


if __name__ == "__main__":
    asyncio.run(create_admin())
