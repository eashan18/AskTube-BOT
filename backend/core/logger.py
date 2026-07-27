"""Logger helper to retrieve configured loggers."""
import logging

from ..config.logging_config import setup_logging
from ..config.settings import get_settings


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured according to project logging settings.

    Calling this will ensure the global logging configuration is applied once.
    """
    settings = get_settings()
    setup_logging(settings)
    return logging.getLogger(name)
