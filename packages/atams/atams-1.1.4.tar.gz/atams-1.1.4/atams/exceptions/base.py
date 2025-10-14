"""
Custom Exceptions for proper HTTP status codes and error messages

Usage in service layer:
    if not user:
        raise NotFoundException("User not found")

    if user.email != input_email:
        raise BadRequestException("Email mismatch")

    if not user.has_permission():
        raise ForbiddenException("Insufficient permission")
"""
from typing import Optional, Any, Dict
from fastapi import status


class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# 4xx Client Errors

class BadRequestException(AppException):
    """400 Bad Request - Client sent invalid data"""

    def __init__(self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class UnauthorizedException(AppException):
    """401 Unauthorized - Authentication required or failed"""

    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenException(AppException):
    """403 Forbidden - User doesn't have permission"""

    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class NotFoundException(AppException):
    """404 Not Found - Resource doesn't exist"""

    def __init__(self, message: str = "Not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ConflictException(AppException):
    """409 Conflict - Resource already exists or conflict with current state"""

    def __init__(self, message: str = "Conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class UnprocessableEntityException(AppException):
    """422 Unprocessable Entity - Validation failed"""

    def __init__(self, message: str = "Unprocessable entity", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


# 5xx Server Errors

class InternalServerException(AppException):
    """500 Internal Server Error - Something went wrong"""

    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class ServiceUnavailableException(AppException):
    """503 Service Unavailable - External service is down"""

    def __init__(self, message: str = "Service unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)
