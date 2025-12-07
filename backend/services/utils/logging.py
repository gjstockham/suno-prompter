"""Logging utilities for the Suno Prompter application."""

import logging
from ..config import config

# Configure logging
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        logging.Logger: A configured logger instance
    """
    return logging.getLogger(name)
