"""
Logging System for AURA v2
Configurable structured logging with request tracking

Features:
- Enable/disable via LOGGING_ENABLED config
- Structured JSON logging
- Request ID tracking
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Colored console output
- File logging support
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from atams.config.base import AtamsBaseSettings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add request_id if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    logging_enabled: bool = True,
    log_level: str = "INFO",
    debug: bool = False,
    log_to_file: bool = False,
    log_file_path: Optional[str] = None
):
    """
    Setup logging configuration with provided parameters

    Args:
        logging_enabled: Enable/disable logging
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: Debug mode (colored output vs JSON)
        log_to_file: Enable file logging
        log_file_path: Path to log file

    Creates two handlers:
    1. Console handler - Colored output for development
    2. File handler - JSON structured logs for production
    """
    if not logging_enabled:
        # Disable all logging
        logging.disable(logging.CRITICAL)
        return

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    logger.handlers.clear()

    # Console Handler (Colored for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))

    if debug:
        # Development: Colored output
        console_format = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Production: JSON output
        console_format = JSONFormatter()

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File Handler (JSON for production)
    if log_to_file and log_file_path:
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)  # Only INFO and above to file
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)


def setup_logging_from_settings(settings: 'AtamsBaseSettings'):
    """
    Setup logging from settings object

    Args:
        settings: Settings instance with LOGGING_* config

    Example:
        from atams.logging import setup_logging_from_settings
        from app.core.config import settings

        setup_logging_from_settings(settings)
    """
    setup_logging(
        logging_enabled=settings.LOGGING_ENABLED,
        log_level=settings.LOG_LEVEL,
        debug=settings.DEBUG,
        log_to_file=settings.LOG_TO_FILE,
        log_file_path=settings.LOG_FILE_PATH
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={'extra_data': {'user_id': 123}})
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding request context

    Usage:
        logger = get_logger(__name__)
        request_logger = LoggerAdapter(logger, {"request_id": "abc-123"})
        request_logger.info("Processing request")
    """

    def process(self, msg, kwargs):
        # Add request_id to all log records
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        kwargs['extra']['request_id'] = self.extra.get('request_id', 'N/A')

        return msg, kwargs
