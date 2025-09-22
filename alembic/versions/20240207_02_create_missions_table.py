"""Create missions table."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20240207_02"
down_revision = "20240207_01"
branch_labels = None
depends_on = None


MISSION_STATUS_VALUES = (
    "draft",
    "scheduled",
    "in_progress",
    "completed",
    "cancelled",
)


def upgrade() -> None:
    mission_status_enum = sa.Enum(  # type: ignore[arg-type]
        *MISSION_STATUS_VALUES,
        name="missionstatus",
        native_enum=False,
        length=50,
    )
    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            mission_status_enum,
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("code", name="uq_missions_code"),
        sa.CheckConstraint(
            "(starts_at IS NULL OR ends_at IS NULL) OR starts_at <= ends_at",
            name="ck_missions_schedule_order",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_missions_owner_id_users",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_missions_code", "missions", ["code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_missions_code", table_name="missions")
    op.drop_table("missions")
