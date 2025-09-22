"""Version endpoint exposing application metadata."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_app_version


router = APIRouter(tags=["version"])


@router.get("/version", summary="Application version information")
def read_version() -> dict[str, str]:
    """Return the semantic version string for the running application."""

    return {"version": get_app_version()}


__all__ = ["router"]

