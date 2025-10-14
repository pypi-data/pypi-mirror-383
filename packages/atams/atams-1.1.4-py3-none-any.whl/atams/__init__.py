"""
ATAMS - Advanced Toolkit for Application Management System
Universal toolkit untuk semua AURA (Atams Universal Runtime Architecture) projects
"""

__version__ = "1.1.4"

# Export main components
from atams.config import AtamsBaseSettings, get_database_url
from atams.db import Base, get_db, init_database, BaseRepository
from atams.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
    InternalServerException,
    ServiceUnavailableException,
    setup_exception_handlers,
)
from atams.schemas import DataResponse, PaginationResponse, ResponseBase, ErrorResponse
from atams.logging import setup_logging, setup_logging_from_settings, get_logger
from atams.api import health_router

__all__ = [
    # Version
    "__version__",

    # Config
    "AtamsBaseSettings",
    "get_database_url",

    # Database
    "Base",
    "get_db",
    "init_database",
    "BaseRepository",

    # API
    "health_router",

    # Exceptions
    "AppException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "UnprocessableEntityException",
    "InternalServerException",
    "ServiceUnavailableException",
    "setup_exception_handlers",

    # Schemas
    "DataResponse",
    "PaginationResponse",
    "ResponseBase",
    "ErrorResponse",

    # Logging
    "setup_logging",
    "setup_logging_from_settings",
    "get_logger",
]
