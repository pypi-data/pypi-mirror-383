"""
Logging System
=============
Structured logging with colored console and JSON file output.

Usage:
    from atams.logging import setup_logging, get_logger, setup_logging_from_settings

    # Setup logging
    setup_logging_from_settings(settings)

    # Get logger in your module
    logger = get_logger(__name__)
    logger.info("Hello, world!")
"""
from atams.logging.setup import (
    setup_logging,
    setup_logging_from_settings,
    get_logger,
    ColoredFormatter,
    JSONFormatter,
)

__all__ = [
    "setup_logging",
    "setup_logging_from_settings",
    "get_logger",
    "ColoredFormatter",
    "JSONFormatter",
]
