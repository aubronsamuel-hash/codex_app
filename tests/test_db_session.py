"""Tests for database session helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.db import session as session_module
from app.db.session import get_db, session_scope


def test_get_db_yields_and_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_session = MagicMock()
    monkeypatch.setattr(session_module, "SessionLocal", lambda: mock_session)

    generator = get_db()
    returned_session = next(generator)
    assert returned_session is mock_session

    generator.close()
    mock_session.close.assert_called_once()


def test_session_scope_commits_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_session = MagicMock()
    monkeypatch.setattr(session_module, "SessionLocal", lambda: mock_session)

    with session_scope() as scoped_session:
        assert scoped_session is mock_session

    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()


def test_session_scope_rolls_back_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_session = MagicMock()
    monkeypatch.setattr(session_module, "SessionLocal", lambda: mock_session)

    with pytest.raises(RuntimeError):
        with session_scope():
            raise RuntimeError("boom")

    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
