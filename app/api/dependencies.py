from functools import lru_cache

from app.scan_engine.factory import create_scan_runner
from app.scan_engine.runner import ScanRunner


@lru_cache
def get_scan_runner() -> ScanRunner:
    return create_scan_runner()
