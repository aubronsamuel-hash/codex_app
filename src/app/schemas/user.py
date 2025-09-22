"""Pydantic models for user data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Common properties shared across user schemas."""

    email: EmailStr


class UserCreate(UserBase):
    """Payload for creating a new user account."""

    password: str = Field(min_length=8, max_length=128)


class UserLogin(UserBase):
    """Payload for authenticating a user."""

    password: str = Field(min_length=1, max_length=128)


class UserRead(UserBase):
    """Public representation of a user."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


__all__ = ["UserBase", "UserCreate", "UserLogin", "UserRead"]
