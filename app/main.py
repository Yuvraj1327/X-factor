"""
app/main.py
────────────
FastAPI application entry point for Visarjan Ghat Watch.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Visarjan Ghat Watch API", env=settings.APP_ENV)
    if settings.WHATSAPP_DRY_RUN:
        logger.warning(
            "DRY RUN MODE is enabled — WhatsApp messages will NOT be sent to Meta. "
            "Set WHATSAPP_DRY_RUN=false in production only after Meta approval."
        )
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Visarjan Ghat Watch — BMC Backend",
    description=(
        "Backend API for the Bhopal Impact Lab Track 2 project. "
        "Provides water-quality analysis, BMC admin dashboard, and WhatsApp citizen service."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,   # Disable Swagger in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(api_router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "dry_run": settings.WHATSAPP_DRY_RUN,
    }
