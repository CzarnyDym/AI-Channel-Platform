from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChannelCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    external_id: str = Field(min_length=1, max_length=255)
    platform: str = Field(default="youtube", min_length=1, max_length=50)


class ChannelRead(ChannelCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
