from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scan import Scan, ScanStatus
from app.models.scan_step import ScanStep, ScanStepStatus


@dataclass(frozen=True)
class StepResult:
    status: ScanStepStatus
    progress_percentage: int = 100
    processed_items: int | None = None
    total_items: int | None = None
    skip_reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        allowed_statuses = {
            ScanStepStatus.COMPLETED,
            ScanStepStatus.SKIPPED,
        }
        if self.status not in allowed_statuses:
            raise ValueError(
                "Handlers must return a completed or skipped result"
            )
        if not 0 <= self.progress_percentage <= 100:
            raise ValueError("Step progress must be between 0 and 100")
        if self.status == ScanStepStatus.SKIPPED and not self.skip_reason:
            raise ValueError("Skipped steps require a skip reason")


@dataclass(frozen=True)
class ScanExecutionContext:
    database: Session
    scan: Scan
    step: ScanStep
    steps: Sequence[ScanStep]
    completion_timestamp: datetime


class ScanStepHandler(Protocol):
    def execute(self, context: ScanExecutionContext) -> StepResult:
        ...


@dataclass(frozen=True)
class ScanRunResult:
    scan_id: UUID
    claimed: bool
    status: ScanStatus | None
