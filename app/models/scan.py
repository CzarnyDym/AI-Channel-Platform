from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanMode(str, Enum):
    LATEST = "latest"
    POPULAR = "popular"
    LATEST_VS_POPULAR = "latest_vs_popular"
    RECENT_PERIOD = "recent_period"
    FULL_CHANNEL = "full_channel"
    PLAYLIST = "playlist"


class Scan(Base):
    __tablename__ = "scans"
    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_scans_progress_percentage",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    channel_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[ScanStatus] = mapped_column(
        SqlEnum(
            ScanStatus,
            name="scan_status",
            native_enum=False,
            values_callable=lambda statuses: [
                scan_status.value for scan_status in statuses
            ],
        ),
        default=ScanStatus.PENDING,
        index=True,
    )
    mode: Mapped[ScanMode] = mapped_column(
        SqlEnum(
            ScanMode,
            name="scan_mode",
            native_enum=False,
            values_callable=lambda modes: [mode.value for mode in modes],
        ),
        default=ScanMode.LATEST,
    )
    scope: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
    )
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    current_step: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    pipeline_version: Mapped[str] = mapped_column(
        String(50),
        default="scan-manifest-v1",
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    channel: Mapped["Channel"] = relationship(back_populates="scans")
    steps: Mapped[list["ScanStep"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="ScanStep.position",
    )
    report: Mapped["Report | None"] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        uselist=False,
    )
