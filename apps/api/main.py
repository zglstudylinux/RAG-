"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.api.routes.ask import router as ask_router
from apps.api.routes.health import router as health_router
from apps.api.routes.ingest import router as ingest_router
from ragkb import __version__
from ragkb.config import get_settings
from ragkb.core.errors import ConfigurationError
from ragkb.core.factory import build_store


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
    app.state.store = build_store(settings)

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(
        request: Request, exc: ConfigurationError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(ask_router)
    return app


app = create_app()
