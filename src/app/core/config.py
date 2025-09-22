"""Application configuration helpers for metadata values."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import tomllib

APP_VERSION = "0.1.0"


def _extract_version(config: Mapping[str, Any]) -> str | None:
    """Return the application version string from a parsed pyproject mapping."""

    tool = config.get("tool")
    if isinstance(tool, Mapping):
        poetry = tool.get("poetry")
        if isinstance(poetry, Mapping):
            version = poetry.get("version")
            if isinstance(version, str) and version.strip():
                return version.strip()

    project = config.get("project")
    if isinstance(project, Mapping):
        version = project.get("version")
        if isinstance(version, str) and version.strip():
            return version.strip()

    version = config.get("version")
    if isinstance(version, str) and version.strip():
        return version.strip()

    return None


def _load_pyproject(path: Path) -> Mapping[str, Any] | None:
    """Load a pyproject.toml file if it exists and is valid TOML."""

    if not path.is_file():
        return None

    try:
        with path.open("rb") as buffer:
            return tomllib.load(buffer)
    except (OSError, tomllib.TOMLDecodeError):
        return None


def get_app_version(pyproject_path: Path | None = None) -> str:
    """Resolve the application version from pyproject metadata or defaults."""

    if pyproject_path is None:
        pyproject_path = Path(__file__).resolve().parents[4] / "pyproject.toml"

    config = _load_pyproject(pyproject_path)
    if config:
        version = _extract_version(config)
        if version:
            return version

    return APP_VERSION


__all__ = ["APP_VERSION", "get_app_version"]

