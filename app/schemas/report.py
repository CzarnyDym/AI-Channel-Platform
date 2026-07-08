from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scan_id: UUID
    report_type: str
    schema_version: str
    content: dict[str, Any]
    created_at: datetime
