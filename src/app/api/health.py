"""Health endpoint returning service metadata."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response payload for the health check."""

    status: str = Field(description="Overall service status indicator.")
    service: str = Field(description="Identifier for the running service.")


@router.get("/health", response_model=HealthResponse, summary="Service status check")
def health_check() -> HealthResponse:
    """Return a simple readiness indicator for liveness probes."""

    return HealthResponse(status="ok", service="codex_app")
