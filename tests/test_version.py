"""Tests for the version endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import get_settings


def test_version_endpoint_exposes_application_version() -> None:
    """The /version route should return the configured version string."""

    client = TestClient(create_app())
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": get_settings().app_version}
