"""
Common Schemas
=============
Pydantic schemas for standardized API responses.

Usage:
    from atams.schemas import ResponseBase, DataResponse, PaginationResponse

    response = DataResponse(
        success=True,
        message="User created",
        data=user
    )
"""
from atams.schemas.response import (
    ResponseBase,
    DataResponse,
    PaginationResponse,
    ErrorResponse,
)

__all__ = [
    "ResponseBase",
    "DataResponse",
    "PaginationResponse",
    "ErrorResponse",
]
