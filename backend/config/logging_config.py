"""Logging configuration utilities."""
from logging.config import dictConfig
from typing import Dict

from ..config.settings import Settings, get_settings


DEFAULT_LOGGING: Dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


def setup_logging(settings: Settings | None = None) -> None:
    """Configure Python logging using a dict configuration.

    Args:
        settings: Optional Settings instance to read `LOG_LEVEL`.
    """
    if settings is None:
        settings = get_settings()

    cfg = DEFAULT_LOGGING.copy()
    # update default level from settings if present
    try:
        level = settings.LOG_LEVEL.upper()
        cfg["handlers"]["console"]["level"] = level
        cfg["root"]["level"] = level
    except Exception:
        pass

    dictConfig(cfg)
