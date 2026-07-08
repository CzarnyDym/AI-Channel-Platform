from datetime import datetime, timezone
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    Uuid,
    create_engine,
    inspect,
    select,
)


def test_migration_upgrades_and_downgrades_sqlite(tmp_path) -> None:
    database_path = tmp_path / "migration-test.db"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert {
        "alembic_version",
        "channels",
        "reports",
        "scan_steps",
        "scans",
    } <= set(inspector.get_table_names())
    assert {
        "mode",
        "scope",
        "progress_percentage",
        "pipeline_version",
        "started_at",
        "finished_at",
    } <= {
        column["name"] for column in inspector.get_columns("scans")
    }
    engine.dispose()

    command.check(config)
    command.downgrade(config, "base")

    engine = create_engine(database_url)
    remaining_tables = set(inspect(engine).get_table_names())
    assert "channels" not in remaining_tables
    assert "scans" not in remaining_tables
    engine.dispose()


def test_migration_upgrades_existing_foundation_schema(tmp_path) -> None:
    database_path = tmp_path / "foundation-migration-test.db"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    engine = create_engine(database_url)
    metadata = MetaData()
    channels = Table(
        "channels",
        metadata,
        Column("id", Uuid(), primary_key=True),
        Column("name", String(255), nullable=False),
        Column("external_id", String(255), nullable=False),
        Column("platform", String(50), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )
    scans = Table(
        "scans",
        metadata,
        Column("id", Uuid(), primary_key=True),
        Column(
            "channel_id",
            Uuid(),
            ForeignKey("channels.id"),
            nullable=False,
        ),
        Column("status", String(20), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
    )
    metadata.create_all(engine)

    channel_id = uuid4()
    scan_id = uuid4()
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            channels.insert().values(
                id=channel_id,
                name="Existing Channel",
                external_id="existing-channel",
                platform="youtube",
                created_at=now,
            )
        )
        connection.execute(
            scans.insert().values(
                id=scan_id,
                channel_id=channel_id,
                status="pending",
                created_at=now,
                updated_at=now,
            )
        )
    engine.dispose()

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    scan_columns = {
        column["name"] for column in inspector.get_columns("scans")
    }
    assert {"mode", "scope", "progress_percentage"} <= scan_columns
    assert {"reports", "scan_steps"} <= set(inspector.get_table_names())
    with engine.connect() as connection:
        migrated_scan = connection.execute(
            select(scans.c.id, scans.c.status).where(
                scans.c.id == scan_id
            )
        ).one()
    assert migrated_scan.status == "pending"
    engine.dispose()
