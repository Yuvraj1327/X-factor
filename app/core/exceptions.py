"""
app/core/exceptions.py
───────────────────────
Domain exceptions and FastAPI exception handlers.
"""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class UnauthorizedError(AppError):
    status_code = 401
    detail = "Authentication required"


class ForbiddenError(AppError):
    status_code = 403
    detail = "Insufficient permissions"


class ConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class ValidationError(AppError):
    status_code = 422
    detail = "Validation error"


class AdvisoryStateError(AppError):
    """Raised when advisory workflow rules are violated."""
    status_code = 409


class StaleDataError(AppError):
    """Raised when water-quality data is too old to support an official advisory."""
    status_code = 422
    detail = "Water-quality data is too old to support an official advisory"


class WhatsAppError(AppError):
    """WhatsApp API errors."""
    status_code = 502


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:  # noqa: ARG001
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
