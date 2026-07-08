from datetime import datetime, timezone
from typing import Any, Sequence

from app.models.scan import Scan
from app.models.scan_step import ScanStep, ScanStepStatus


TECHNICAL_MANIFEST_TYPE = "technical_scan_manifest"
TECHNICAL_MANIFEST_SCHEMA_VERSION = "1.0"
TECHNICAL_MANIFEST_DISCLAIMER = (
    "Technical execution manifest only. No platform data ingestion or "
    "AI processing was performed."
)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _isoformat(value: datetime | None) -> str | None:
    return _as_utc(value).isoformat() if value is not None else None


class TechnicalManifestBuilder:
    report_type = TECHNICAL_MANIFEST_TYPE
    schema_version = TECHNICAL_MANIFEST_SCHEMA_VERSION

    def build(
        self,
        scan: Scan,
        steps: Sequence[ScanStep],
        *,
        completed_step_key: str,
        completed_at: datetime,
    ) -> dict[str, Any]:
        started_at = scan.started_at or completed_at
        duration_ms = max(
            0,
            int(
                (
                    _as_utc(completed_at) - _as_utc(started_at)
                ).total_seconds()
                * 1000
            ),
        )

        step_entries = []
        for step in steps:
            is_completed_step = step.key == completed_step_key
            step_entries.append(
                {
                    "key": step.key,
                    "position": step.position,
                    "status": (
                        ScanStepStatus.COMPLETED.value
                        if is_completed_step
                        else step.status.value
                    ),
                    "started_at": _isoformat(step.started_at),
                    "finished_at": _isoformat(
                        completed_at
                        if is_completed_step
                        else step.finished_at
                    ),
                    "skip_reason": step.skip_reason,
                    "processed_items": step.processed_items,
                    "total_items": step.total_items,
                }
            )

        return {
            "report_type": self.report_type,
            "schema_version": self.schema_version,
            "disclaimer": TECHNICAL_MANIFEST_DISCLAIMER,
            "scan": {
                "id": str(scan.id),
                "channel_id": str(scan.channel_id),
                "mode": scan.mode.value,
                "scope": scan.scope,
                "pipeline_version": scan.pipeline_version,
                "status": "completed",
                "created_at": _isoformat(scan.created_at),
                "started_at": _isoformat(started_at),
                "finished_at": _isoformat(completed_at),
                "duration_ms": duration_ms,
            },
            "steps": step_entries,
        }
