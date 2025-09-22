"""Tests for the Mission model and transitions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.models import Mission, MissionStatus
from app.schemas.mission import MissionCreate, MissionUpdate


def make_times() -> tuple[datetime, datetime]:
    start = datetime.now(tz=UTC).replace(tzinfo=None)
    end = start + timedelta(hours=2)
    return start, end


def test_mission_persists_defaults(db_session):
    start, end = make_times()
    mission = Mission(title="Inspect site", start_time=start, end_time=end)

    db_session.add(mission)
    db_session.commit()
    db_session.refresh(mission)

    assert mission.status is MissionStatus.DRAFT
    assert mission.created_at is not None
    assert mission.updated_at is not None
    assert mission.can_transition_to(MissionStatus.PLANNED)


def test_mission_time_window_enforced(db_session):
    start = datetime.now(tz=UTC).replace(tzinfo=None)
    mission = Mission(title="Invalid window", start_time=start, end_time=start)
    db_session.add(mission)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_mission_happy_path_transitions(db_session):
    start, end = make_times()
    mission = Mission(title="Deployment", start_time=start, end_time=end)
    db_session.add(mission)
    db_session.commit()
    db_session.refresh(mission)

    mission.transition_to(MissionStatus.PLANNED)
    mission.transition_to(MissionStatus.CONFIRMED)
    mission.start()
    mission.finish()

    db_session.commit()
    db_session.refresh(mission)

    assert mission.status is MissionStatus.DONE


def test_mission_invalid_transition_raises(db_session):
    start, end = make_times()
    mission = Mission(title="Cannot skip", start_time=start, end_time=end)
    db_session.add(mission)
    db_session.commit()
    db_session.refresh(mission)

    with pytest.raises(ValueError):
        mission.start()

    mission.transition_to(MissionStatus.PLANNED)
    mission.cancel()
    assert mission.status is MissionStatus.CANCELED

    with pytest.raises(ValueError):
        mission.transition_to(MissionStatus.CONFIRMED)


def test_mission_create_schema_validation():
    start, end = make_times()
    payload = MissionCreate(title="Schema", start_time=start, end_time=end)

    assert payload.status is MissionStatus.DRAFT

    with pytest.raises(ValidationError):
        MissionCreate(title="Schema", start_time=end, end_time=start)


def test_mission_update_schema_validation():
    start, end = make_times()
    payload = MissionUpdate(start_time=start)
    assert payload.start_time == start
    second = MissionUpdate(end_time=end)
    assert second.end_time == end

    with pytest.raises(ValidationError):
        MissionUpdate(start_time=start, end_time=start)
