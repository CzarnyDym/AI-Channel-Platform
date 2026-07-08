"""Create the initial backend and MVP Scan Engine schema.

Revision ID: 0001_mvp_scan_engine
Revises:
Create Date: 2026-07-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_mvp_scan_engine"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


scan_status = sa.Enum(
    "pending",
    "running",
    "completed",
    "failed",
    name="scan_status",
    native_enum=False,
)
scan_mode = sa.Enum(
    "latest",
    "popular",
    "latest_vs_popular",
    "recent_period",
    "full_channel",
    "playlist",
    name="scan_mode",
    native_enum=False,
)
scan_step_status = sa.Enum(
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
    name="scan_step_status",
    native_enum=False,
)


def _create_fresh_schema() -> None:
    op.create_table(
        "channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform",
            "external_id",
            name="uq_channels_platform_external_id",
        ),
    )
    op.create_table(
        "scans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=False),
        sa.Column("status", scan_status, nullable=False),
        sa.Column("mode", scan_mode, nullable=False),
        sa.Column("scope", sa.JSON(), nullable=False),
        sa.Column(
            "progress_percentage",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "current_step",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "pipeline_version",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column(
            "error_code",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_scans_progress_percentage",
        ),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["channels.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scans_channel_id"),
        "scans",
        ["channel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scans_status"),
        "scans",
        ["status"],
        unique=False,
    )
    op.create_table(
        "scan_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("status", scan_step_status, nullable=False),
        sa.Column(
            "progress_percentage",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("processed_items", sa.Integer(), nullable=True),
        sa.Column("total_items", sa.Integer(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column(
            "skip_reason",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "error_code",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_scan_steps_progress_percentage",
        ),
        sa.CheckConstraint(
            "weight > 0",
            name="ck_scan_steps_weight",
        ),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scan_id",
            "key",
            name="uq_scan_steps_scan_id_key",
        ),
    )
    op.create_index(
        op.f("ix_scan_steps_scan_id"),
        "scan_steps",
        ["scan_id"],
        unique=False,
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_id", sa.Uuid(), nullable=False),
        sa.Column(
            "report_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "schema_version",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_id"),
    )
    op.create_index(
        op.f("ix_reports_scan_id"),
        "reports",
        ["scan_id"],
        unique=True,
    )


def _upgrade_foundation_schema(existing_tables: set[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    scan_columns = {
        column["name"] for column in inspector.get_columns("scans")
    }
    scan_checks = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("scans")
    }

    with op.batch_alter_table("scans") as batch_op:
        if "mode" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "mode",
                    scan_mode,
                    nullable=False,
                    server_default="latest",
                )
            )
        if "scope" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "scope",
                    sa.JSON(),
                    nullable=False,
                    server_default=sa.text("'{}'"),
                )
            )
        if "progress_percentage" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "progress_percentage",
                    sa.Integer(),
                    nullable=False,
                    server_default="0",
                )
            )
        if "current_step" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "current_step",
                    sa.String(length=100),
                    nullable=True,
                )
            )
        if "pipeline_version" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "pipeline_version",
                    sa.String(length=50),
                    nullable=False,
                    server_default="scan-manifest-v1",
                )
            )
        if "attempt_count" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "attempt_count",
                    sa.Integer(),
                    nullable=False,
                    server_default="0",
                )
            )
        if "error_code" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "error_code",
                    sa.String(length=100),
                    nullable=True,
                )
            )
        if "error_message" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "error_message",
                    sa.Text(),
                    nullable=True,
                )
            )
        if "started_at" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "started_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )
        if "finished_at" not in scan_columns:
            batch_op.add_column(
                sa.Column(
                    "finished_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )
        if "ck_scans_progress_percentage" not in scan_checks:
            batch_op.create_check_constraint(
                "ck_scans_progress_percentage",
                "progress_percentage >= 0 "
                "AND progress_percentage <= 100",
            )

    inspector = sa.inspect(op.get_bind())
    scan_indexes = {
        index["name"] for index in inspector.get_indexes("scans")
    }
    if op.f("ix_scans_status") not in scan_indexes:
        op.create_index(
            op.f("ix_scans_status"),
            "scans",
            ["status"],
            unique=False,
        )

    if "scan_steps" not in existing_tables:
        op.create_table(
            "scan_steps",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("scan_id", sa.Uuid(), nullable=False),
            sa.Column("key", sa.String(length=100), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("weight", sa.Integer(), nullable=False),
            sa.Column("status", scan_step_status, nullable=False),
            sa.Column(
                "progress_percentage",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column("processed_items", sa.Integer(), nullable=True),
            sa.Column("total_items", sa.Integer(), nullable=True),
            sa.Column("attempt_count", sa.Integer(), nullable=False),
            sa.Column(
                "skip_reason",
                sa.String(length=100),
                nullable=True,
            ),
            sa.Column(
                "error_code",
                sa.String(length=100),
                nullable=True,
            ),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("details", sa.JSON(), nullable=False),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "finished_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.CheckConstraint(
                "progress_percentage >= 0 "
                "AND progress_percentage <= 100",
                name="ck_scan_steps_progress_percentage",
            ),
            sa.CheckConstraint(
                "weight > 0",
                name="ck_scan_steps_weight",
            ),
            sa.ForeignKeyConstraint(
                ["scan_id"],
                ["scans.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "scan_id",
                "key",
                name="uq_scan_steps_scan_id_key",
            ),
        )
        op.create_index(
            op.f("ix_scan_steps_scan_id"),
            "scan_steps",
            ["scan_id"],
            unique=False,
        )

    if "reports" not in existing_tables:
        op.create_table(
            "reports",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("scan_id", sa.Uuid(), nullable=False),
            sa.Column(
                "report_type",
                sa.String(length=100),
                nullable=False,
            ),
            sa.Column(
                "schema_version",
                sa.String(length=50),
                nullable=False,
            ),
            sa.Column("content", sa.JSON(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["scan_id"],
                ["scans.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("scan_id"),
        )
        op.create_index(
            op.f("ix_reports_scan_id"),
            "reports",
            ["scan_id"],
            unique=True,
        )


def upgrade() -> None:
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())
    application_tables = existing_tables & {
        "channels",
        "scans",
        "scan_steps",
        "reports",
    }
    if not application_tables:
        _create_fresh_schema()
        return

    if not {"channels", "scans"} <= application_tables:
        raise RuntimeError(
            "Cannot migrate a partial backend schema without channels "
            "and scans tables"
        )
    _upgrade_foundation_schema(existing_tables)


def downgrade() -> None:
    op.drop_index(op.f("ix_reports_scan_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(
        op.f("ix_scan_steps_scan_id"),
        table_name="scan_steps",
    )
    op.drop_table("scan_steps")
    op.drop_index(op.f("ix_scans_status"), table_name="scans")
    op.drop_index(op.f("ix_scans_channel_id"), table_name="scans")
    op.drop_table("scans")
    op.drop_table("channels")
