"""Tests for the Mission domain model."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Mission, MissionStatus


def test_create_mission_defaults(db_session):
    mission = Mission(code="MSN-001", title="First mission")
    db_session.add(mission)
    db_session.commit()
    db_session.refresh(mission)

    assert mission.status is MissionStatus.DRAFT
    assert mission.created_at is not None
    assert mission.updated_at is not None
    assert mission.can_transition_to(MissionStatus.SCHEDULED)


def test_mission_unique_code_enforced(db_session):
    first = Mission(code="MSN-002", title="Unique code")
    second = Mission(code="MSN-002", title="Duplicate code")
    db_session.add_all([first, second])

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_mission_schedule_constraint(db_session):
    starts_at = datetime.now(tz=timezone.utc)
    ends_at = starts_at - timedelta(hours=1)
    mission = Mission(
        code="MSN-003",
        title="Backwards schedule",
        starts_at=starts_at,
        ends_at=ends_at,
    )
    db_session.add(mission)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_mission_status_transitions(db_session):
    mission = Mission(code="MSN-004", title="Transition control")
    db_session.add(mission)
    db_session.commit()
    db_session.refresh(mission)

    assert mission.can_transition_to(MissionStatus.DRAFT)
    mission.transition_to(MissionStatus.DRAFT)
    db_session.commit()
    db_session.refresh(mission)
    assert mission.status is MissionStatus.DRAFT

    mission.transition_to(MissionStatus.SCHEDULED)
    db_session.commit()
    db_session.refresh(mission)
    assert mission.status is MissionStatus.SCHEDULED

    mission.transition_to(MissionStatus.IN_PROGRESS)
    db_session.commit()
    db_session.refresh(mission)
    assert mission.status is MissionStatus.IN_PROGRESS

    with pytest.raises(ValueError):
        mission.transition_to(MissionStatus.DRAFT)
