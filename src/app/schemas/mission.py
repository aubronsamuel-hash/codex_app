"""Pydantic schemas for missions."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from app.models import MissionStatus


class MissionBase(BaseModel):
    """Fields shared across mission payloads."""

    title: str
    start_time: datetime
    end_time: datetime
    status: MissionStatus = MissionStatus.DRAFT
    notes: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_interval(cls, end_time: datetime, info: ValidationInfo) -> datetime:
        start_time = info.data.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return end_time


class MissionCreate(MissionBase):
    """Payload for creating a mission."""

    pass


class MissionUpdate(BaseModel):
    """Payload for updating mission fields."""

    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[MissionStatus] = None
    notes: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_interval_update(
        cls, end_time: Optional[datetime], info: ValidationInfo
    ) -> Optional[datetime]:
        start_time = info.data.get("start_time")
        if start_time and end_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return end_time


class MissionRead(BaseModel):
    """Serialized mission returned by the API."""

    id: str
    title: str
    start_time: datetime
    end_time: datetime
    status: MissionStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, raw: uuid.UUID | str) -> str:
        return str(raw)


__all__ = [
    "MissionBase",
    "MissionCreate",
    "MissionUpdate",
    "MissionRead",
]
