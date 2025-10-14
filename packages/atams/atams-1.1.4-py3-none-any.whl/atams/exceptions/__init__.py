"""
Exception Handling
=================
Custom exceptions and exception handlers for ATAMS applications.

Usage:
    from atams.exceptions import (
        AppException,
        BadRequestException,
        UnauthorizedException,
        setup_exception_handlers
    )
"""
from atams.exceptions.base import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
    InternalServerException,
    ServiceUnavailableException,
)
from atams.exceptions.handlers import (
    setup_exception_handlers,
    app_exception_handler,
    validation_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)

__all__ = [
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
    # Handlers
    "setup_exception_handlers",
    "app_exception_handler",
    "validation_exception_handler",
    "integrity_exception_handler",
    "sqlalchemy_exception_handler",
    "general_exception_handler",
]
