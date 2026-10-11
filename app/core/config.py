"""
app/core/config.py
──────────────────
Application-wide settings loaded from environment variables / .env file.
Uses pydantic-settings for typed, validated configuration.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Visarjan Ghat Watch"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:changeme@localhost:5432/ghatwatch"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:changeme@localhost:5432/ghatwatch"

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ── Admin Bootstrap ───────────────────────────────────────────────────────
    BOOTSTRAP_ADMIN_EMAIL: str = ""
    BOOTSTRAP_ADMIN_PASSWORD: str = ""

    # ── WhatsApp Cloud API ────────────────────────────────────────────────────
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_GRAPH_API_VERSION: str = "v21.0"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_TEMPLATE_NAME_EN: str = "ghat_advisory_en"
    WHATSAPP_TEMPLATE_NAME_HI: str = "ghat_advisory_hi"
    WHATSAPP_DRY_RUN: bool = True  # Safe default — never send without explicit opt-in

    # ── Data Quality ──────────────────────────────────────────────────────────
    DATA_FRESHNESS_THRESHOLD_DAYS: int = 90

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def whatsapp_api_base(self) -> str:
        return f"https://graph.facebook.com/{self.WHATSAPP_GRAPH_API_VERSION}"

    @property
    def whatsapp_messages_url(self) -> str:
        return f"{self.whatsapp_api_base}/{self.WHATSAPP_PHONE_NUMBER_ID}/messages"


@lru_cache
def get_settings() -> Settings:
    return Settings()
