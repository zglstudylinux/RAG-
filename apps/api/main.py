"""FastAPI application entry point."""

from __future__ import annotations

from importlib.resources import files

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from apps.api.routes.ask import router as ask_router
from apps.api.routes.auth import router as auth_router
from apps.api.routes.documents import router as documents_router
from apps.api.routes.health import router as health_router
from apps.api.routes.ingest import router as ingest_router
from apps.api.routes.users import router as users_router
from ragkb import __version__
from ragkb.config import get_settings
from ragkb.core.errors import ConfigurationError
from ragkb.core.factory import build_store
from ragkb.indexing.user_store import UserStore


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
    app.state.user_store = UserStore(settings.store_path)
    app.state.user_store.ensure_default_user(
        settings.default_admin_username, settings.default_admin_password
    )

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(
        request: Request, exc: ConfigurationError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(ingest_router)
    app.include_router(ask_router)
    app.include_router(documents_router)
    app.include_router(users_router)

    @app.get("/", include_in_schema=False)
    async def index() -> HTMLResponse:
        html = files("ragkb.web").joinpath("index.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    return app


app = create_app()
