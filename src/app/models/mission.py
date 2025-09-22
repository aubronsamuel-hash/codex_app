"""Mission domain model with status transitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import ClassVar, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

if TYPE_CHECKING:  # pragma: no cover
    from .user import User


class MissionStatus(str, Enum):
    """Possible lifecycle states for a mission."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Mission(Base):
    """Mission persisted entity representing planned work."""

    __tablename__ = "missions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_missions_code"),
        CheckConstraint(
            "(starts_at IS NULL OR ends_at IS NULL) OR starts_at <= ends_at",
            name="ck_missions_schedule_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[MissionStatus] = mapped_column(
        SQLEnum(MissionStatus, native_enum=False, length=50),
        nullable=False,
        default=MissionStatus.DRAFT,
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner: Mapped["User | None"] = relationship("User", backref="missions")

    _TRANSITIONS: ClassVar[dict[MissionStatus, set[MissionStatus]]] = {
        MissionStatus.DRAFT: {MissionStatus.SCHEDULED, MissionStatus.CANCELLED},
        MissionStatus.SCHEDULED: {
            MissionStatus.IN_PROGRESS,
            MissionStatus.CANCELLED,
        },
        MissionStatus.IN_PROGRESS: {
            MissionStatus.COMPLETED,
            MissionStatus.CANCELLED,
        },
        MissionStatus.COMPLETED: set(),
        MissionStatus.CANCELLED: set(),
    }

    def can_transition_to(self, new_status: MissionStatus) -> bool:
        """Return True when the transition is allowed from the current status."""

        if new_status == self.status:
            return True
        return new_status in self._TRANSITIONS[self.status]

    def transition_to(self, new_status: MissionStatus) -> None:
        """Update mission status if the transition is valid, otherwise raise."""

        if new_status == self.status:
            return
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition mission {self.code} from {self.status.value} to {new_status.value}"
            )
        self.status = new_status


__all__ = ["Mission", "MissionStatus"]
