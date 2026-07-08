from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.channel import Channel
from app.models.report import Report
from app.models.scan import Scan, ScanStatus
from app.models.scan_step import ScanStep
from app.scan_engine.pipeline import PIPELINE_VERSION
from app.scan_engine.registry import StepRegistry
from app.schemas.scan import ScanCreate


def create_scan(
    database: Session,
    channel_id: UUID,
    scan_data: ScanCreate,
    registry: StepRegistry,
) -> Scan | None:
    channel = database.get(Channel, channel_id)
    if channel is None:
        return None

    registry.validate()
    scan = Scan(
        channel_id=channel.id,
        status=ScanStatus.PENDING,
        mode=scan_data.mode,
        scope=scan_data.scope,
        pipeline_version=PIPELINE_VERSION,
        steps=[
            ScanStep(
                key=definition.key,
                position=definition.position,
                weight=definition.weight,
            )
            for definition in registry.definitions
        ],
    )
    database.add(scan)
    database.commit()
    database.refresh(scan)
    scan.steps
    return scan


def get_scan(database: Session, scan_id: UUID) -> Scan | None:
    return database.scalar(
        select(Scan)
        .where(Scan.id == scan_id)
        .options(selectinload(Scan.steps))
    )


def get_report(database: Session, scan_id: UUID) -> Report | None:
    return database.scalar(
        select(Report).where(Report.scan_id == scan_id)
    )
