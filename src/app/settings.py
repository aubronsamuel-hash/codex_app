"""Application configuration helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration values for the FastAPI service."""

    app_name: str = Field(default="Codex App", description="Human friendly service name.")
    app_env: Literal["development", "staging", "production", "test"] = Field(
        default="development", description="Execution environment identifier."
    )
    app_version: str = Field(default="0.1.0", description="Published application version string.")
    host: str = Field(default="127.0.0.1", description="Default bind host for the ASGI server.")
    port: int = Field(default=8000, description="Default bind port for the ASGI server.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables with sensible defaults."""

    return Settings(
        app_name=os.getenv("APP_NAME", Settings.model_fields["app_name"].default),
        app_env=os.getenv("APP_ENV", Settings.model_fields["app_env"].default),
        app_version=os.getenv("APP_VERSION", Settings.model_fields["app_version"].default),
        host=os.getenv("HOST", Settings.model_fields["host"].default),
        port=int(os.getenv("PORT", Settings.model_fields["port"].default)),
    )


__all__ = ["Settings", "get_settings"]

