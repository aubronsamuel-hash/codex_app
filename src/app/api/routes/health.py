"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health", summary="Service liveness indicator")
def get_health() -> dict[str, str]:
    """Return a simple health status payload."""

    return {"status": "ok"}


__all__ = ["router"]

