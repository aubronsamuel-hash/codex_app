"""Health endpoint returning service metadata."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response payload for the health check."""

    status: str = Field(description="Overall service status indicator.")
    service: str = Field(description="Identifier for the running service.")
    environment: str = Field(description="Execution environment for the backend service.")


@router.get("/health", response_model=HealthResponse, summary="Service status check")
def health_check(request: Request) -> HealthResponse:
    """Return a simple readiness indicator for liveness probes."""

    settings = request.app.state.settings
    return HealthResponse(status="ok", service=settings.app_name, environment=settings.app_env)
