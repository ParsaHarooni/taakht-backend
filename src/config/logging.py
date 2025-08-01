"""Logging configuration for Taakht backend.

This module provides centralized logging configuration with different log levels
and formats for different environments.
"""

import logging
import logging.config
from pathlib import Path

from .settings import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Logging configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "detailed",
            "filename": logs_dir / "taakht.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": logs_dir / "taakht_error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # Root logger
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "tortoise": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "src": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
    },
}


def setup_logging():
    """Setup logging configuration."""
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger(__name__)
        logger.info("Logging configuration loaded successfully")
        return logger
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL.upper()),
            format=settings.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(logs_dir / "taakht_fallback.log"),
            ],
        )
        logger = logging.getLogger(__name__)
        logger.error("Failed to load logging configuration: %s", e)
        return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name or __name__)
