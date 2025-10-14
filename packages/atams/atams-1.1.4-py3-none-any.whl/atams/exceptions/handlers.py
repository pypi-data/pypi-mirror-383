"""
Global Exception Handler
Converts exceptions to proper JSON responses with status codes
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from atams.exceptions import AppException
from atams.logging import get_logger

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors (422)"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "details": {"errors": errors}
        }
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (409)"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "message": "Database constraint violation",
            "details": {"error": "Duplicate entry or constraint violation"}
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors (500)"""
    # Log the actual database error with details
    logger.error(
        f"Database error: {str(exc)}",
        exc_info=True,
        extra={
            'extra_data': {
                'error_type': type(exc).__name__,
                'path': request.url.path,
                'method': request.method
            }
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Database error occurred",
            "details": {"error": str(exc.orig) if hasattr(exc, 'orig') else str(exc)}
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions (500)"""
    # Log all unhandled exceptions with full traceback
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            'extra_data': {
                'error_type': type(exc).__name__,
                'path': request.url.path,
                'method': request.method
            }
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "details": {"error": str(exc)}
        }
    )


def setup_exception_handlers(app):
    """
    Setup all exception handlers for FastAPI application

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        from atams.exceptions import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
