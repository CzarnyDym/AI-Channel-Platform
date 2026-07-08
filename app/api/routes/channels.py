from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.channel import ChannelCreate, ChannelRead
from app.services import channel_service


router = APIRouter(prefix="/channels", tags=["channels"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
def create_channel(
    channel_data: ChannelCreate,
    database: DatabaseSession,
) -> ChannelRead:
    try:
        return channel_service.create_channel(database, channel_data)
    except channel_service.ChannelAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("/{channel_id}", response_model=ChannelRead)
def get_channel(
    channel_id: UUID,
    database: DatabaseSession,
) -> ChannelRead:
    channel = channel_service.get_channel(database, channel_id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return channel
