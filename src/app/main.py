"""Application factory for the Codex backend."""

from fastapi import FastAPI

from .api import health_router

APP_TITLE = "Codex App"
APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Instantiate the FastAPI application with core routes."""

    app = FastAPI(title=APP_TITLE, version=APP_VERSION)
    app.include_router(health_router)
    return app


app = create_app()
