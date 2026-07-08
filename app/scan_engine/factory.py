from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.scan_engine.pipeline import build_default_registry
from app.scan_engine.runner import ScanRunner


def create_scan_runner(
    session_factory: Callable[[], Session] = SessionLocal,
) -> ScanRunner:
    return ScanRunner(
        session_factory=session_factory,
        registry=build_default_registry(),
    )
