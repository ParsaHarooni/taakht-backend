"""Configuration module for Taakht backend.

This module provides centralized configuration management including settings,
database configuration, logging setup, and environment-specific configurations.
"""

from .settings import settings, get_settings
from .database import init_db, close_db, get_tortoise_config
from .logging import setup_logging, get_logger

__all__ = [
    "settings",
    "get_settings",
    "init_db",
    "close_db",
    "get_tortoise_config",
    "setup_logging",
    "get_logger",
]
