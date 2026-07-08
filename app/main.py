from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import channels, health, scans
from app.core.config import get_settings
from app.core.database import init_db


def create_app(*, initialize_database: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if initialize_database:
            init_db()
        yield

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.include_router(health.router)
    application.include_router(channels.router)
    application.include_router(scans.router)
    return application


app = create_app()
