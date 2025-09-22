"""API router exports."""

from .auth import router as auth_router
from .health import router as health_router
from .version import router as version_router

__all__ = ["auth_router", "health_router", "version_router"]
