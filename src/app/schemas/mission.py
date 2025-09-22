"""Pydantic schemas for mission data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models import MissionStatus


class MissionBase(BaseModel):
    """Common fields shared by mission payloads."""

    code: str = Field(min_length=3, max_length=40, pattern=r"^[A-Z0-9-]+$")
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=2000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @field_validator("ends_at")
    @classmethod
    def _validate_schedule(cls, ends_at: datetime | None, values: dict[str, object]) -> datetime | None:
        """Ensure end date is not before the start date when both are provided."""

        start = values.get("starts_at")
        if start and ends_at and ends_at < start:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        return ends_at


class MissionCreate(MissionBase):
    """Payload for creating a mission record."""

    status: MissionStatus = MissionStatus.DRAFT
    owner_id: int | None = None


class MissionUpdate(BaseModel):
    """Payload for updating mutable mission fields."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=2000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: MissionStatus | None = None
    owner_id: int | None = None

    @field_validator("ends_at")
    @classmethod
    def _validate_schedule(cls, ends_at: datetime | None, values: dict[str, object]) -> datetime | None:
        start = values.get("starts_at")
        if start and ends_at and ends_at < start:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        return ends_at


class MissionRead(MissionBase):
    """Public representation of a mission."""

    id: int
    status: MissionStatus
    owner_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


__all__ = [
    "MissionBase",
    "MissionCreate",
    "MissionUpdate",
    "MissionRead",
]
