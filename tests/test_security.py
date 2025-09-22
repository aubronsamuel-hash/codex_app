"""Unit tests for security helpers."""

from __future__ import annotations

import jwt
import pytest

from app.security import (
    TokenError,
    create_access_token,
    decode_token,
    iter_tokens,
    hash_password,
    verify_password,
)
from app.settings import get_settings


def test_hash_and_verify_password() -> None:
    """Hashes should not equal the original password and must verify correctly."""

    password = "s3cretpass"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_encode_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Encoding and decoding tokens should round-trip the payload."""

    monkeypatch.setenv("AUTH_SECRET", "unit-test-secret")
    monkeypatch.setenv("AUTH_ACCESS_TTL", "60")
    monkeypatch.setenv("AUTH_REFRESH_TTL", "120")
    get_settings.cache_clear()

    token = create_access_token("42", ttl_seconds=15)
    payload = decode_token(token)

    assert payload.sub == "42"
    assert payload.type == "access"

    get_settings.cache_clear()


def test_decode_token_rejects_invalid_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_SECRET", "unit-test-secret")
    get_settings.cache_clear()

    with pytest.raises(TokenError):
        decode_token("not-a-token")

    get_settings.cache_clear()


def test_decode_token_rejects_malformed_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_SECRET", "unit-test-secret")
    get_settings.cache_clear()

    token = jwt.encode({"foo": "bar"}, "unit-test-secret", algorithm="HS256")

    with pytest.raises(TokenError):
        decode_token(token)

    get_settings.cache_clear()


def test_iter_tokens_yields_pair(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_SECRET", "unit-test-secret")
    monkeypatch.setenv("AUTH_ACCESS_TTL", "60")
    monkeypatch.setenv("AUTH_REFRESH_TTL", "120")
    get_settings.cache_clear()

    access, refresh = list(iter_tokens("123"))
    assert access != refresh

    get_settings.cache_clear()
