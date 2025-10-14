"""
Middleware for ATAMS
- Request ID tracking
- Request/Response logging
- Request timing
"""
import time
import uuid
from typing import Callable, Optional, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Optional logger - will work without it
logger: Optional[Any] = None

try:
    from atams.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    pass


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request

    Features:
    - Generate UUID for each request
    - Add to request state (accessible in endpoints)
    - Add to response headers
    - Log request/response with request ID
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add to request state
        request.state.request_id = request_id

        # Use logger directly (if available)
        request_logger = logger

        # Log incoming request
        start_time = time.time()
        if request_logger:
            request_logger.info(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    'extra_data': {
                        'method': request.method,
                        'path': request.url.path,
                        'client_ip': request.client.host if request.client else None,
                        'user_agent': request.headers.get('user-agent', 'unknown')
                    }
                }
            )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            if request_logger:
                request_logger.error(
                    f"Request failed with exception: {str(e)}",
                    exc_info=True,
                    extra={'extra_data': {'exception_type': type(e).__name__}}
                )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        # Log response
        if request_logger:
            request_logger.info(
                f"Request completed: {response.status_code} in {process_time:.4f}s",
                extra={
                    'extra_data': {
                        'status_code': response.status_code,
                        'process_time': f"{process_time:.4f}s"
                    }
                }
            )

        return response
