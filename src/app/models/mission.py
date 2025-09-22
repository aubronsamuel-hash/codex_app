"""Mission domain model and state transitions."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import CheckConstraint, DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class MissionStatus(str, enum.Enum):
    """Possible lifecycle states for a mission."""

    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELED = "CANCELED"


def utcnow() -> datetime:
    """Return the current UTC datetime.

    Using a helper keeps the value patchable in tests when needed.
    """

    return datetime.now(tz=UTC).replace(tzinfo=None)


class MissionMixin:
    """Shared transition helpers for missions."""

    _ALLOWED_TRANSITIONS: ClassVar[dict[MissionStatus, set[MissionStatus]]] = {
        MissionStatus.DRAFT: {
            MissionStatus.PLANNED,
            MissionStatus.CONFIRMED,
            MissionStatus.CANCELED,
        },
        MissionStatus.PLANNED: {
            MissionStatus.CONFIRMED,
            MissionStatus.CANCELED,
        },
        MissionStatus.CONFIRMED: {
            MissionStatus.IN_PROGRESS,
            MissionStatus.CANCELED,
        },
        MissionStatus.IN_PROGRESS: {MissionStatus.DONE},
        MissionStatus.DONE: set(),
        MissionStatus.CANCELED: set(),
    }

    def can_transition_to(self, nxt: MissionStatus) -> bool:
        """Return True when the transition to ``nxt`` is allowed."""

        current = MissionStatus(self.status)
        return nxt in self._ALLOWED_TRANSITIONS.get(current, set())

    def transition_to(self, nxt: MissionStatus) -> None:
        """Update the mission status after validating the transition."""

        if not self.can_transition_to(nxt):  # pragma: no branch - single guard
            raise ValueError(f"invalid transition {self.status} -> {nxt}")
        self.status = nxt

    def start(self) -> None:
        """Move the mission to the in-progress state."""

        self.transition_to(MissionStatus.IN_PROGRESS)

    def finish(self) -> None:
        """Mark the mission as completed."""

        self.transition_to(MissionStatus.DONE)

    def cancel(self) -> None:
        """Cancel the mission."""

        self.transition_to(MissionStatus.CANCELED)


class Mission(Base, MissionMixin):
    """Persisted mission with scheduling metadata."""

    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_missions_time_range"),
        Index("ix_missions_time_range", "start_time", "end_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    status: Mapped[MissionStatus] = mapped_column(
        Enum(MissionStatus, name="mission_status", native_enum=False, validate_strings=True),
        nullable=False,
        default=MissionStatus.DRAFT,
        server_default=MissionStatus.DRAFT.value,
    )
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
        onupdate=utcnow,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Mission {self.id} {self.title} {self.status}>"


__all__ = ["Mission", "MissionStatus"]
