from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_scan_runner
from app.core.database import get_db
from app.scan_engine.runner import ScanRunner
from app.schemas.report import ReportRead
from app.schemas.scan import ScanCreate, ScanRead
from app.services import scan_service


router = APIRouter(tags=["scans"])
DatabaseSession = Annotated[Session, Depends(get_db)]
Runner = Annotated[ScanRunner, Depends(get_scan_runner)]


@router.post(
    "/channels/{channel_id}/scans",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scan(
    channel_id: UUID,
    background_tasks: BackgroundTasks,
    database: DatabaseSession,
    runner: Runner,
    scan_data: ScanCreate | None = None,
) -> ScanRead:
    scan = scan_service.create_scan(
        database,
        channel_id,
        scan_data or ScanCreate(),
        runner.registry,
    )
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    background_tasks.add_task(runner.run, scan.id)
    return scan


@router.get("/scans/{scan_id}", response_model=ScanRead)
def get_scan(
    scan_id: UUID,
    database: DatabaseSession,
) -> ScanRead:
    scan = scan_service.get_scan(database, scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )
    return scan


@router.get("/scans/{scan_id}/report", response_model=ReportRead)
def get_scan_report(
    scan_id: UUID,
    database: DatabaseSession,
) -> ReportRead:
    scan = scan_service.get_scan(database, scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    report = scan_service.get_report(database, scan_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Scan report is not available",
        )
    return report
