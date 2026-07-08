from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.channel import Channel
from app.schemas.channel import ChannelCreate


class ChannelAlreadyExistsError(ValueError):
    pass


def create_channel(
    database: Session,
    channel_data: ChannelCreate,
) -> Channel:
    existing_channel = database.scalar(
        select(Channel).where(
            Channel.platform == channel_data.platform,
            Channel.external_id == channel_data.external_id,
        )
    )
    if existing_channel is not None:
        raise ChannelAlreadyExistsError(
            "A channel with this platform and external ID already exists"
        )

    channel = Channel(**channel_data.model_dump())
    database.add(channel)
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise ChannelAlreadyExistsError(
            "A channel with this platform and external ID already exists"
        ) from error
    database.refresh(channel)
    return channel


def get_channel(database: Session, channel_id: UUID) -> Channel | None:
    return database.get(Channel, channel_id)
