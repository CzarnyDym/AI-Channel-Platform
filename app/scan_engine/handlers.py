from app.models.report import Report
from app.models.scan_step import ScanStepStatus
from app.scan_engine.manifest import TechnicalManifestBuilder
from app.scan_engine.types import ScanExecutionContext, StepResult


class ValidateScopeHandler:
    def execute(self, context: ScanExecutionContext) -> StepResult:
        if not isinstance(context.scan.scope, dict):
            raise ValueError("Scan scope must be an object")
        return StepResult(
            status=ScanStepStatus.COMPLETED,
            details={"scope_validated": True},
        )


class NotImplementedHandler:
    def execute(self, context: ScanExecutionContext) -> StepResult:
        return StepResult(
            status=ScanStepStatus.SKIPPED,
            skip_reason="not_implemented",
        )


class BuildTechnicalManifestHandler:
    def __init__(self, builder: TechnicalManifestBuilder) -> None:
        self._builder = builder

    def execute(self, context: ScanExecutionContext) -> StepResult:
        content = self._builder.build(
            context.scan,
            context.steps,
            completed_step_key=context.step.key,
            completed_at=context.completion_timestamp,
        )
        context.database.add(
            Report(
                scan_id=context.scan.id,
                report_type=self._builder.report_type,
                schema_version=self._builder.schema_version,
                content=content,
            )
        )
        return StepResult(
            status=ScanStepStatus.COMPLETED,
            details={
                "report_type": self._builder.report_type,
                "schema_version": self._builder.schema_version,
            },
        )
