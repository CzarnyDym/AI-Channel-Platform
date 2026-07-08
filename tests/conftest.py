from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.dependencies import get_scan_runner
from app.core.database import Base, get_db
from app.main import create_app
from app.scan_engine.factory import create_scan_runner


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    testing_engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(
        bind=testing_engine,
        class_=Session,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=testing_engine)
    yield testing_session
    Base.metadata.drop_all(bind=testing_engine)
    testing_engine.dispose()


@pytest.fixture
def client(
    session_factory: sessionmaker[Session],
) -> Iterator[TestClient]:
    application = create_app(initialize_database=False)

    def override_get_db() -> Iterator[Session]:
        database = session_factory()
        try:
            yield database
        finally:
            database.close()

    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_scan_runner] = lambda: (
        create_scan_runner(session_factory)
    )

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()
