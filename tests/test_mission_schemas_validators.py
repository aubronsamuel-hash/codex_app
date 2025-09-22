from datetime import datetime, timedelta
from app.schemas.mission import MissionCreate, MissionUpdate, MissionRead
from app.models.mission import MissionStatus


def test_create_schema_valid_interval():
    now = datetime.utcnow()
    mc = MissionCreate(
        title="T",
        start_time=now,
        end_time=now + timedelta(hours=1),
        status=MissionStatus.DRAFT,
        notes=None,
    )
    assert mc.end_time > mc.start_time


def test_create_schema_invalid_interval_raises():
    now = datetime.utcnow()
    try:
        MissionCreate(
            title="T",
            start_time=now,
            end_time=now - timedelta(minutes=5),
        )
        assert False, "Expected validation error for invalid interval"
    except Exception as exc:
        assert "end_time must be after start_time" in str(exc)


def test_update_schema_invalid_interval_raises():
    now = datetime.utcnow()
    try:
        MissionUpdate(
            start_time=now,
            end_time=now - timedelta(minutes=1),
        )
        assert False, "Expected validation error for invalid interval on update"
    except Exception as exc:
        assert "end_time must be after start_time" in str(exc)


def test_update_schema_valid_interval_ok():
    now = datetime.utcnow()
    mu = MissionUpdate(
        start_time=now,
        end_time=now + timedelta(minutes=10),
        status=MissionStatus.PLANNED,
    )
    assert mu.end_time > mu.start_time


def test_read_schema_from_attributes_mapping():
    now = datetime.utcnow()

    class Obj:
        pass

    o = Obj()
    o.id = "00000000-0000-0000-0000-000000000000"
    o.title = "T"
    o.start_time = now
    o.end_time = now + timedelta(hours=2)
    o.status = MissionStatus.CONFIRMED
    o.notes = None
    o.created_at = now
    o.updated_at = now

    mr = MissionRead.model_validate(o, from_attributes=True)
    assert mr.id == o.id
    assert mr.title == o.title
    assert mr.status == MissionStatus.CONFIRMED
