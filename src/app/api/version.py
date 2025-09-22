"""Version endpoint exposing the running application version."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field


router = APIRouter(tags=["version"])


class VersionResponse(BaseModel):
    """Response payload describing the running release version."""

    version: str = Field(description="Semantic version of the backend service.")


@router.get("/version", response_model=VersionResponse, summary="Application version information")
def read_version(request: Request) -> VersionResponse:
    """Return the current semantic version string from settings."""

    settings = request.app.state.settings
    return VersionResponse(version=settings.app_version)

