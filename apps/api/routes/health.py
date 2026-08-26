"""Health and status endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from ragkb import __version__
from ragkb.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    """Report service status and a sanitized config summary (no secrets)."""
    return {
        "status": "ok",
        "service": "ragkb",
        "version": __version__,
        "config": get_settings().public_summary,
    }
