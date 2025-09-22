"""Tests for the health endpoint and application factory."""

from fastapi.testclient import TestClient

from app.main import app, create_app
from app.settings import get_settings


def test_health_endpoint_returns_expected_payload() -> None:
    """The /health endpoint should respond with a deterministic payload."""

    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    expected = {
        "status": "ok",
        "service": get_settings().app_name,
        "environment": get_settings().app_env,
    }
    assert response.json() == expected


def test_module_level_app_is_reusable() -> None:
    """The global app instance should also expose the health endpoint."""

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
