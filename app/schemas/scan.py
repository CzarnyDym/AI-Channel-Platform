from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.scan import ScanMode, ScanStatus
from app.models.scan_step import ScanStepStatus


class ScanCreate(BaseModel):
    mode: ScanMode = ScanMode.LATEST
    scope: dict[str, Any] = Field(default_factory=dict)


class ScanStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    position: int
    weight: int
    status: ScanStepStatus
    progress_percentage: int
    processed_items: int | None
    total_items: int | None
    attempt_count: int
    skip_reason: str | None
    error_code: str | None
    error_message: str | None
    details: dict[str, Any]
    started_at: datetime | None
    finished_at: datetime | None


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel_id: UUID
    status: ScanStatus
    mode: ScanMode
    scope: dict[str, Any]
    progress_percentage: int
    current_step: str | None
    pipeline_version: str
    attempt_count: int
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    steps: list[ScanStepRead]
