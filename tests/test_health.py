"""Tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_ok() -> None:
    """The /health endpoint returns a simple ok payload."""

    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
