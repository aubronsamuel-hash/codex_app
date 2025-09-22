"""JWT helpers for access and refresh tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Generator

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError

from ..schemas import TokenPayload
from ..settings import get_settings

ALGORITHM = "HS256"


class TokenError(Exception):
    """Base error for token validation failures."""


class TokenExpiredError(TokenError):
    """Raised when a token is expired."""


def _issue_token(subject: str, token_type: str, ttl_seconds: int) -> str:
    """Generate a signed JWT for the given subject and lifetime."""

    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM)


def create_access_token(subject: str | int, ttl_seconds: int | None = None) -> str:
    """Create an access token for the provided subject."""

    settings = get_settings()
    lifetime = ttl_seconds or settings.auth_access_ttl
    return _issue_token(str(subject), "access", lifetime)


def create_refresh_token(subject: str | int, ttl_seconds: int | None = None) -> str:
    """Create a refresh token for the provided subject."""

    settings = get_settings()
    lifetime = ttl_seconds or settings.auth_refresh_ttl
    return _issue_token(str(subject), "refresh", lifetime)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a token, returning its payload."""

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:  # pragma: no cover - exercised via integration tests
        raise TokenExpiredError("Token has expired") from exc
    except InvalidTokenError as exc:
        raise TokenError("Token is invalid") from exc

    try:
        return TokenPayload(**payload)
    except ValidationError as exc:
        raise TokenError("Token payload is malformed") from exc


def iter_tokens(subject: str | int) -> Generator[str, None, None]:
    """Yield both access and refresh tokens for a subject."""

    yield create_access_token(subject)
    yield create_refresh_token(subject)


__all__ = [
    "ALGORITHM",
    "TokenError",
    "TokenExpiredError",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "iter_tokens",
]
