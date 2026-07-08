import os
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = field(
        default_factory=lambda: os.getenv(
            "APP_NAME",
            "AI Channel Platform API",
        )
    )
    app_version: str = field(
        default_factory=lambda: os.getenv("APP_VERSION", "0.1.0")
    )
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "sqlite+pysqlite:///./ai_channel_platform.db",
        )
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
