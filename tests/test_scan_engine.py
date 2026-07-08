import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.channel import Channel
from app.models.report import Report
from app.models.scan import Scan, ScanMode, ScanStatus
from app.models.scan_step import ScanStep, ScanStepStatus
from app.scan_engine.handlers import BuildTechnicalManifestHandler
from app.scan_engine.manifest import TechnicalManifestBuilder
from app.scan_engine.pipeline import build_default_registry
from app.scan_engine.registry import StepDefinition, StepRegistry
from app.scan_engine.runner import ScanRunner
from app.scan_engine.types import ScanExecutionContext, StepResult
from app.schemas.scan import ScanCreate
from app.services.scan_service import create_scan


FORBIDDEN_MANIFEST_TERMS = (
    "insight",
    "recommendation",
    "prediction",
    "evidence",
)


def create_pending_scan(
    session_factory: sessionmaker[Session],
    registry: StepRegistry,
) -> UUID:
    with session_factory() as database:
        channel = Channel(
            name="Engine Test Channel",
            external_id="engine-test-channel",
        )
        database.add(channel)
        database.commit()
        database.refresh(channel)

        scan = create_scan(
            database,
            channel.id,
            ScanCreate(
                mode=ScanMode.RECENT_PERIOD,
                scope={"days": 30},
            ),
            registry,
        )
        assert scan is not None
        return scan.id


def test_runner_completes_technical_manifest(
    session_factory: sessionmaker[Session],
) -> None:
    registry = build_default_registry()
    scan_id = create_pending_scan(session_factory, registry)
    runner = ScanRunner(session_factory, registry)

    result = runner.run(scan_id)

    assert result.claimed is True
    assert result.status == ScanStatus.COMPLETED

    with session_factory() as database:
        scan = database.get(Scan, scan_id)
        assert scan is not None
        assert scan.status == ScanStatus.COMPLETED
        assert scan.progress_percentage == 100
        assert scan.current_step is None

        steps = database.scalars(
            select(ScanStep)
            .where(ScanStep.scan_id == scan_id)
            .order_by(ScanStep.position)
        ).all()
        assert len(steps) == 7
        assert steps[0].status == ScanStepStatus.COMPLETED
        assert steps[-1].status == ScanStepStatus.COMPLETED

        skipped_steps = [
            step
            for step in steps
            if step.status == ScanStepStatus.SKIPPED
        ]
        assert len(skipped_steps) == 5
        assert {
            step.skip_reason for step in skipped_steps
        } == {"not_implemented"}

        report = database.scalar(
            select(Report).where(Report.scan_id == scan_id)
        )
        assert report is not None
        assert report.report_type == "technical_scan_manifest"
        manifest_text = json.dumps(report.content).lower()
        for forbidden_term in FORBIDDEN_MANIFEST_TERMS:
            assert forbidden_term not in manifest_text
        assert report.content["scan"]["mode"] == "recent_period"
        assert report.content["scan"]["scope"] == {"days": 30}
        assert report.content["scan"]["pipeline_version"] == (
            "scan-manifest-v1"
        )


def test_runner_does_not_claim_completed_scan(
    session_factory: sessionmaker[Session],
) -> None:
    registry = build_default_registry()
    scan_id = create_pending_scan(session_factory, registry)
    runner = ScanRunner(session_factory, registry)

    first_result = runner.run(scan_id)
    second_result = runner.run(scan_id)

    assert first_result.claimed is True
    assert second_result.claimed is False
    assert second_result.status == ScanStatus.COMPLETED


class CustomTechnicalHandler:
    def execute(self, context: ScanExecutionContext) -> StepResult:
        return StepResult(
            status=ScanStepStatus.COMPLETED,
            details={"custom_check": "passed"},
        )


class RecordingHandler:
    def __init__(self, delegate: object, progress_values: list[int]) -> None:
        self._delegate = delegate
        self._progress_values = progress_values

    def execute(self, context: ScanExecutionContext) -> StepResult:
        self._progress_values.append(
            context.scan.progress_percentage
        )
        return self._delegate.execute(context)  # type: ignore[attr-defined]


def test_scan_progress_is_monotonic(
    session_factory: sessionmaker[Session],
) -> None:
    progress_values: list[int] = []
    registry = StepRegistry()
    for definition in build_default_registry().definitions:
        registry.register(
            StepDefinition(
                key=definition.key,
                position=definition.position,
                weight=definition.weight,
                handler=RecordingHandler(
                    definition.handler,
                    progress_values,
                ),
            )
        )
    scan_id = create_pending_scan(session_factory, registry)

    result = ScanRunner(session_factory, registry).run(scan_id)

    assert result.status == ScanStatus.COMPLETED
    assert progress_values == sorted(progress_values)
    assert progress_values[0] == 0
    with session_factory() as database:
        scan = database.get(Scan, scan_id)
        assert scan is not None
        assert scan.progress_percentage == 100


def test_registry_extends_pipeline_without_runner_changes(
    session_factory: sessionmaker[Session],
) -> None:
    registry = build_default_registry()
    registry.register(
        StepDefinition(
            key="custom_technical_check",
            position=65,
            weight=5,
            handler=CustomTechnicalHandler(),
        )
    )
    scan_id = create_pending_scan(session_factory, registry)

    result = ScanRunner(session_factory, registry).run(scan_id)

    assert result.status == ScanStatus.COMPLETED
    with session_factory() as database:
        custom_step = database.scalar(
            select(ScanStep).where(
                ScanStep.scan_id == scan_id,
                ScanStep.key == "custom_technical_check",
            )
        )
        assert custom_step is not None
        assert custom_step.status == ScanStepStatus.COMPLETED
        assert custom_step.details == {"custom_check": "passed"}


def test_registry_requires_report_builder_as_final_step() -> None:
    registry = build_default_registry()
    registry.register(
        StepDefinition(
            key="late_step",
            position=80,
            weight=5,
            handler=CustomTechnicalHandler(),
        )
    )

    try:
        registry.validate()
    except ValueError as error:
        assert str(error) == (
            "The build_report step must be the final pipeline step"
        )
    else:
        raise AssertionError("Invalid pipeline order was accepted")


class FailingHandler:
    def execute(self, context: ScanExecutionContext) -> StepResult:
        raise RuntimeError("Sensitive internal failure details")


def build_failing_registry() -> StepRegistry:
    registry = StepRegistry()
    default_registry = build_default_registry()
    for definition in default_registry.definitions:
        handler = (
            FailingHandler()
            if definition.key == "normalize_data"
            else definition.handler
        )
        registry.register(
            StepDefinition(
                key=definition.key,
                position=definition.position,
                weight=definition.weight,
                handler=handler,
            )
        )
    return registry


def test_handler_failure_persists_safe_failure_state(
    session_factory: sessionmaker[Session],
) -> None:
    registry = build_failing_registry()
    scan_id = create_pending_scan(session_factory, registry)

    result = ScanRunner(session_factory, registry).run(scan_id)

    assert result.status == ScanStatus.FAILED
    with session_factory() as database:
        scan = database.get(Scan, scan_id)
        assert scan is not None
        assert scan.status == ScanStatus.FAILED
        assert scan.error_code == "scan_execution_failed"
        assert scan.error_message == "Scan execution failed"
        assert "Sensitive" not in scan.error_message

        failed_step = database.scalar(
            select(ScanStep).where(
                ScanStep.scan_id == scan_id,
                ScanStep.key == "normalize_data",
            )
        )
        assert failed_step is not None
        assert failed_step.status == ScanStepStatus.FAILED
        assert failed_step.error_code == "handler_execution_failed"

        report = database.scalar(
            select(Report).where(Report.scan_id == scan_id)
        )
        assert report is None


def test_report_builder_is_isolated_from_report_model() -> None:
    assert not any(
        name.startswith("build") for name in Report.__dict__
    )
    handler = BuildTechnicalManifestHandler(
        TechnicalManifestBuilder()
    )
    assert handler is not None
