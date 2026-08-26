"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routes.health import router as health_router
from ragkb import __version__
from ragkb.config import get_settings


def create_app() -> FastAPI:
    """Build the FastAPI application with all routers wired up."""
    settings = get_settings()
    app = FastAPI(
        title="ragkb",
        version=__version__,
        description=(
            "Reusable, pluggable RAG knowledge base for chip SDK technical documentation."
        ),
    )
    app.state.settings = settings
    app.include_router(health_router)
    return app


app = create_app()
