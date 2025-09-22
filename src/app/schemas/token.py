"""Token schemas for authentication."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Representation of a JWT payload."""

    sub: str
    type: Literal["access", "refresh"]
    exp: int
    iat: int


class TokenPair(BaseModel):
    """Response containing both access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class AccessToken(BaseModel):
    """Response containing a refreshed access token."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshRequest(BaseModel):
    """Request payload carrying a refresh token."""

    refresh_token: str


__all__ = ["AccessToken", "RefreshRequest", "TokenPair", "TokenPayload"]
