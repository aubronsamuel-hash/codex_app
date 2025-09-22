"""Password hashing helpers."""

from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a secure password hash."""

    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Validate a clear-text password against a stored hash."""

    return _pwd_context.verify(password, password_hash)


__all__ = ["hash_password", "verify_password"]
