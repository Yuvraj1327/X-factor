"""
app/core/logging.py
────────────────────
Structured logging configuration using structlog.
Secrets are never logged — phone numbers and tokens are masked.
"""
from __future__ import annotations

import logging
import re
import sys

import structlog

from app.core.config import get_settings

settings = get_settings()

_REDACT_PATTERNS = [
    (re.compile(r"(Bearer\s+)\S+", re.IGNORECASE), r"\1[REDACTED]"),
    (re.compile(r"(\+91)\d{10}"), r"\1**********"),
    (re.compile(r'"password"\s*:\s*"[^"]*"'), '"password": "[REDACTED]"'),
    (re.compile(r'"access_token"\s*:\s*"[^"]*"'), '"access_token": "[REDACTED]"'),
]


def _redact_processor(logger, method, event_dict):  # noqa: ARG001
    message = event_dict.get("event", "")
    for pattern, replacement in _REDACT_PATTERNS:
        message = pattern.sub(replacement, str(message))
    event_dict["event"] = message
    return event_dict


def configure_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors = [
        structlog.stdlib.add_log_level,
        # NOTE: add_logger_name requires stdlib logger; omit for PrintLoggerFactory
        structlog.processors.TimeStamper(fmt="iso"),
        _redact_processor,
    ]

    if settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )

    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(message)s",
    )


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
