"""Cursor pagination shared by collection endpoints."""
from __future__ import annotations

import base64
from typing import Generic, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel


ItemT = TypeVar("ItemT")


class Pagina(BaseModel, Generic[ItemT]):
    """A cursor-paginated collection response."""

    items: list[ItemT]
    total: int
    next_cursor: str | None


def decode_cursor(cursor: str | None) -> int:
    """Decode an opaque, URL-safe cursor containing a non-negative offset."""
    if cursor is None:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True)
        value = raw.decode("ascii")
        if not value.isdecimal():
            raise ValueError("offset non numerico")
        offset = int(value)
    except (UnicodeEncodeError, UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Cursor di paginazione non valido.") from exc
    return offset


def encode_cursor(offset: int) -> str:
    """Encode an offset without padding, so it is safe in a query string."""
    return base64.urlsafe_b64encode(str(offset).encode("ascii")).decode("ascii").rstrip("=")
