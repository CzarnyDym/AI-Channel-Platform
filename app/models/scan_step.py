from __future__ import annotations

from datetime import datetime
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
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ScanStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScanStep(Base):
    __tablename__ = "scan_steps"
    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "key",
            name="uq_scan_steps_scan_id_key",
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_scan_steps_progress_percentage",
        ),
        CheckConstraint("weight > 0", name="ck_scan_steps_weight"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    scan_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)
    status: Mapped[ScanStepStatus] = mapped_column(
        SqlEnum(
            ScanStepStatus,
            name="scan_step_status",
            native_enum=False,
            values_callable=lambda statuses: [
                step_status.value for step_status in statuses
            ],
        ),
        default=ScanStepStatus.PENDING,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    total_items: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    skip_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scan: Mapped["Scan"] = relationship(back_populates="steps")
