from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Channel(Base):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint(
            "platform",
            "external_id",
            name="uq_channels_platform_external_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255))
    external_id: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(
        String(50),
        default="youtube",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    scans: Mapped[list["Scan"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
    )
