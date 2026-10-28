"""Consistent API error envelopes while retaining FastAPI's original detail."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _http_error(detail: Any) -> tuple[str, str]:
    if isinstance(detail, dict) and isinstance(detail.get("error"), str):
        message = detail.get("message")
        return detail["error"], message if isinstance(message, str) else detail["error"]
    if isinstance(detail, str):
        return "http_error", detail
    return "http_error", "La richiesta non può essere elaborata."


def install_error_handlers(app: FastAPI) -> None:
    """Install handlers that add a stable envelope without changing ``detail``."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException,
    ) -> JSONResponse:
        del request
        code, message = _http_error(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "error": {"code": code, "message": message, "field": None},
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError,
    ) -> JSONResponse:
        del request
        errors = exc.errors()
        location = errors[0].get("loc", []) if errors else []
        field = str(location[-1]) if location else None
        message = (
            f"Il valore del campo '{field}' non è valido."
            if field else "La richiesta contiene dati non validi."
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {"code": "validation_error", "message": message, "field": field},
                "detail": errors,
            },
        )
