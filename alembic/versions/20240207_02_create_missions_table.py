"""Create missions table."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20240207_02"
down_revision = "20240207_01"
branch_labels = None
depends_on = None


MISSION_STATUSES = (
    "DRAFT",
    "PLANNED",
    "CONFIRMED",
    "IN_PROGRESS",
    "DONE",
    "CANCELED",
)


def upgrade() -> None:
    mission_status_enum = sa.Enum(
        *MISSION_STATUSES,
        name="mission_status",
        native_enum=False,
        validate_strings=True,
    )
    op.create_table(
        "missions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "status",
            mission_status_enum,
            nullable=False,
            server_default=sa.text("'DRAFT'"),
        ),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("start_time < end_time", name="ck_missions_time_range"),
    )
    op.create_index(
        "ix_missions_time_range",
        "missions",
        ["start_time", "end_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_missions_time_range", table_name="missions")
    op.drop_table("missions")
