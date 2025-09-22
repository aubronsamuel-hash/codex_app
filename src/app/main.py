"""Application factory for the Codex backend."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from .api import health_router, version_router
from .settings import get_settings


def create_app() -> FastAPI:
    """Instantiate the FastAPI application with core routes."""

    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.state.settings = settings
    app.include_router(health_router)
    app.include_router(version_router)
    return app


app = create_app()
