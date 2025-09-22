"""Tests for the version endpoint and helpers."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import APP_VERSION, get_app_version
from app.main import create_app


def test_version_present() -> None:
    """GET /version responds with a payload containing the version string."""

    client = TestClient(create_app())
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["version"]


def test_version_semver_like() -> None:
    """The returned version loosely matches a semantic version pattern."""

    client = TestClient(create_app())
    version = client.get("/version").json()["version"]
    assert re.match(r"^[0-9]+\.[0-9]+\.[0-9]+", version)


@pytest.mark.parametrize(
    "content, expected",
    [
        ("[tool.poetry]\nversion='1.2.3'\n", "1.2.3"),
        ("[project]\nversion='2.0.0'\n", "2.0.0"),
        ("[project]\nversion=''\n", APP_VERSION),
        ("[tool]\npoetry='ignored'\n[project]\nversion='4.5.6'\n", "4.5.6"),
        ("version='3.4.5'\n", "3.4.5"),
        ("tool = 'string'\nversion='5.6.7'\n", "5.6.7"),
        ("[tool.poetry]\nname='demo'\n", APP_VERSION),
    ],
)
def test_get_app_version_handles_pyproject_variants(
    tmp_path: Path, content: str, expected: str
) -> None:
    """The helper reads from pyproject.toml falling back to the default constant."""

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(content, encoding="utf-8")
    assert get_app_version(pyproject) == expected


def test_get_app_version_missing_file(tmp_path: Path) -> None:
    """Missing pyproject files should fall back to the static APP_VERSION value."""

    missing = tmp_path / "pyproject.toml"
    assert get_app_version(missing) == APP_VERSION


def test_get_app_version_invalid_toml(tmp_path: Path) -> None:
    """Invalid TOML content should be handled gracefully."""

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("invalid = ['unterminated'", encoding="utf-8")
    assert get_app_version(pyproject) == APP_VERSION
