"""Database configuration and initialization for Taakht backend.

This module handles Tortoise ORM database configuration, connection management,
and initialization for different database backends (SQLite, PostgreSQL).
"""

import logging
from pathlib import Path

from tortoise import Tortoise

from .settings import settings

logger = logging.getLogger(__name__)


# Database configuration for Tortoise ORM
def get_tortoise_config():
    """Get Tortoise ORM configuration."""
    if "sqlite" in settings.DATABASE_URL:
        # SQLite configuration
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")

        # Ensure the database directory exists
        db_dir = Path(db_path).parent
        if db_dir != Path("."):
            db_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created database directory: %s", db_dir)

        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {
                        "file_path": db_path,
                        "journal_mode": "WAL",
                    },
                }
            },
            "apps": {
                "models": {
                    "models": [
                        "src.models.user",
                        "src.models.item",
                        "src.models.trade",
                        "src.models.category",
                        "src.models.item_image",
                        "src.models.role",
                    ],
                    "default_connection": "default",
                },
            },
            "use_tz": False,
            "timezone": "UTC",
        }

    # PostgreSQL configuration
    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "database": settings.DATABASE_URL.rsplit("/", maxsplit=1)[-1],
                    "host": "localhost",
                    "password": None,
                    "port": 5432,
                    "user": "postgres",
                    "dsn": settings.DATABASE_URL,
                },
            }
        },
        "apps": {
            "models": {
                "models": [
                    "src.models.user",
                    "src.models.item",
                    "src.models.trade",
                    "src.models.category",
                    "src.models.item_image",
                    "src.models.role",
                ],
                "default_connection": "default",
            },
        },
        "use_tz": False,
        "timezone": "UTC",
    }


async def init_db():
    """Initialize database connection and create tables."""
    try:
        config = get_tortoise_config()
        await Tortoise.init(config=config)
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        raise


async def close_db():
    """Close database connections."""
    try:
        await Tortoise.close_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Failed to close database connections: %s", e)
        raise


def get_fastapi_tortoise_config():
    """Get Tortoise ORM configuration for FastAPI integration."""
    return {
        "db_url": settings.DATABASE_URL,
        "modules": {
            "models": [
                "src.models.user",
                "src.models.item",
                "src.models.trade",
                "src.models.category",
                "src.models.item_image",
                "src.models.role",
            ]
        },
        "generate_schemas": True,
        "add_exception_handlers": True,
    }
