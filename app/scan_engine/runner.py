import logging
from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.scan import Scan, ScanStatus
from app.models.scan_step import ScanStep, ScanStepStatus
from app.scan_engine.registry import StepRegistry
from app.scan_engine.types import (
    ScanExecutionContext,
    ScanRunResult,
    StepResult,
)


logger = logging.getLogger(__name__)
SessionFactory = Callable[[], Session]
Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ScanRunner:
    def __init__(
        self,
        session_factory: SessionFactory,
        registry: StepRegistry,
        *,
        clock: Clock = utc_now,
    ) -> None:
        self._session_factory = session_factory
        self.registry = registry
        self.registry.validate()
        self._clock = clock

    def run(self, scan_id: UUID) -> ScanRunResult:
        if not self._claim(scan_id):
            return ScanRunResult(
                scan_id=scan_id,
                claimed=False,
                status=self._get_status(scan_id),
            )

        with self._session_factory() as database:
            scan: Scan | None = None
            try:
                scan = self._load_scan(database, scan_id)
                for index, definition in enumerate(
                    self.registry.definitions
                ):
                    step = self._get_step(scan, definition.key)
                    self._start_step(database, scan, step)

                    completion_timestamp = self._clock()
                    result = definition.handler.execute(
                        ScanExecutionContext(
                            database=database,
                            scan=scan,
                            step=step,
                            steps=tuple(scan.steps),
                            completion_timestamp=completion_timestamp,
                        )
                    )
                    self._complete_step(
                        scan,
                        step,
                        result,
                        completion_timestamp,
                    )

                    is_last_step = (
                        index == len(self.registry.definitions) - 1
                    )
                    if is_last_step:
                        database.flush()
                        self._complete_scan(
                            database,
                            scan,
                            completion_timestamp,
                        )
                    database.commit()

                return ScanRunResult(
                    scan_id=scan_id,
                    claimed=True,
                    status=ScanStatus.COMPLETED,
                )
            except Exception:
                database.rollback()
                logger.exception("Scan %s failed", scan_id)
                self._mark_failed(
                    scan_id,
                    scan.current_step if scan is not None else None,
                )
                return ScanRunResult(
                    scan_id=scan_id,
                    claimed=True,
                    status=ScanStatus.FAILED,
                )

    def _claim(self, scan_id: UUID) -> bool:
        claimed_at = self._clock()
        with self._session_factory() as database:
            result = database.execute(
                update(Scan)
                .where(
                    Scan.id == scan_id,
                    Scan.status == ScanStatus.PENDING,
                )
                .values(
                    status=ScanStatus.RUNNING,
                    started_at=claimed_at,
                    finished_at=None,
                    error_code=None,
                    error_message=None,
                    attempt_count=Scan.attempt_count + 1,
                )
            )
            database.commit()
            return result.rowcount == 1

    def _get_status(self, scan_id: UUID) -> ScanStatus | None:
        with self._session_factory() as database:
            return database.scalar(
                select(Scan.status).where(Scan.id == scan_id)
            )

    @staticmethod
    def _load_scan(database: Session, scan_id: UUID) -> Scan:
        scan = database.get(Scan, scan_id)
        if scan is None:
            raise LookupError(f"Scan {scan_id} does not exist")
        scan.steps
        return scan

    @staticmethod
    def _get_step(scan: Scan, key: str) -> ScanStep:
        for step in scan.steps:
            if step.key == key:
                return step
        raise LookupError(f"Scan step '{key}' does not exist")

    def _start_step(
        self,
        database: Session,
        scan: Scan,
        step: ScanStep,
    ) -> None:
        step.status = ScanStepStatus.RUNNING
        step.started_at = self._clock()
        step.finished_at = None
        step.attempt_count += 1
        step.skip_reason = None
        step.error_code = None
        step.error_message = None
        scan.current_step = step.key
        database.commit()

    @staticmethod
    def _complete_step(
        scan: Scan,
        step: ScanStep,
        result: StepResult,
        completed_at: datetime,
    ) -> None:
        step.status = result.status
        step.progress_percentage = result.progress_percentage
        step.processed_items = result.processed_items
        step.total_items = result.total_items
        step.skip_reason = result.skip_reason
        step.details = result.details
        step.finished_at = completed_at
        scan.progress_percentage = ScanRunner._calculate_progress(
            scan.steps
        )

    @staticmethod
    def _calculate_progress(steps: list[ScanStep]) -> int:
        total_weight = sum(step.weight for step in steps)
        if total_weight == 0:
            return 0
        weighted_progress = sum(
            step.weight * step.progress_percentage for step in steps
        )
        return round(weighted_progress / total_weight)

    @staticmethod
    def _complete_scan(
        database: Session,
        scan: Scan,
        completed_at: datetime,
    ) -> None:
        report_exists = database.scalar(
            select(Report.id).where(Report.scan_id == scan.id)
        )
        if report_exists is None:
            raise RuntimeError("Scan cannot complete without a report")
        scan.status = ScanStatus.COMPLETED
        scan.progress_percentage = 100
        scan.current_step = None
        scan.finished_at = completed_at

    def _mark_failed(
        self,
        scan_id: UUID,
        step_key: str | None,
    ) -> None:
        failed_at = self._clock()
        with self._session_factory() as database:
            scan = database.get(Scan, scan_id)
            if scan is None:
                return

            if step_key is not None:
                step = database.scalar(
                    select(ScanStep).where(
                        ScanStep.scan_id == scan_id,
                        ScanStep.key == step_key,
                    )
                )
                if step is not None:
                    step.status = ScanStepStatus.FAILED
                    step.finished_at = failed_at
                    step.error_code = "handler_execution_failed"
                    step.error_message = "Step execution failed"

            scan.status = ScanStatus.FAILED
            scan.finished_at = failed_at
            scan.error_code = "scan_execution_failed"
            scan.error_message = "Scan execution failed"
            database.commit()
