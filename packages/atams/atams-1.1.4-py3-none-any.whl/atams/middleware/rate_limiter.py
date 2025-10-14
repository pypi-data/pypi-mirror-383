"""
Rate Limiting System for ATAMS
In-memory rate limiting based on IP address

Features:
- Configurable requests per window
- In-memory storage (no external dependencies)
- Automatic cleanup of expired entries
- Can be enabled/disabled via config

Usage in user project (app/main.py):
    from atams.middleware import create_rate_limit_middleware
    from app.core.config import settings

    app.add_middleware(create_rate_limit_middleware(settings))
"""
import time
from typing import Dict, Tuple, TYPE_CHECKING, Optional, Any
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

if TYPE_CHECKING:
    from atams.config.base import AtamsBaseSettings
    from logging import LoggerAdapter

# Optional logger - will use print if not available
logger: Optional[Any] = None
try:
    from atams.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    pass


class RateLimiter:
    """
    In-memory rate limiter using sliding window

    Storage format:
    {
        "client_ip": (request_count, window_start_time)
    }
    """

    def __init__(self, requests: int = 100, window: int = 60):
        """
        Initialize rate limiter

        Args:
            requests: Maximum requests allowed per window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for client

        Args:
            client_id: Client identifier (usually IP address)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        count, window_start = self.clients[client_id]

        # Check if window has expired
        if current_time - window_start >= self.window:
            # Reset window
            self.clients[client_id] = (1, current_time)
            return True, self.requests - 1

        # Window still active
        if count >= self.requests:
            # Rate limit exceeded
            return False, 0

        # Increment counter
        self.clients[client_id] = (count + 1, window_start)
        return True, self.requests - (count + 1)

    def cleanup_expired(self):
        """Remove expired entries to prevent memory leak"""
        current_time = time.time()
        expired_clients = [
            client_id for client_id, (_, window_start) in self.clients.items()
            if current_time - window_start >= self.window * 2
        ]

        for client_id in expired_clients:
            del self.clients[client_id]


def create_rate_limit_middleware(settings: 'AtamsBaseSettings'):
    """
    Factory function to create RateLimitMiddleware with settings

    Args:
        settings: Settings instance with RATE_LIMIT_* config

    Returns:
        RateLimitMiddleware class configured with settings

    Example:
        from atams.middleware import create_rate_limit_middleware
        from app.core.config import settings

        app.add_middleware(create_rate_limit_middleware(settings))
    """

    # Create rate limiter instance with settings
    rate_limiter = RateLimiter(
        requests=settings.RATE_LIMIT_REQUESTS,
        window=settings.RATE_LIMIT_WINDOW
    )

    class RateLimitMiddleware(BaseHTTPMiddleware):
        """
        Middleware to enforce rate limiting

        Features:
        - Rate limit based on client IP
        - Add rate limit headers to response
        - Return 429 when limit exceeded
        - Periodic cleanup of expired entries
        """

        def __init__(self, app):
            super().__init__(app)
            self.cleanup_counter = 0

        async def dispatch(self, request: Request, call_next) -> Response:
            # Skip rate limiting if disabled
            if not settings.RATE_LIMIT_ENABLED:
                return await call_next(request)

            # Skip rate limiting for docs and openapi
            if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
                return await call_next(request)

            # Get client IP
            client_ip = request.client.host if request.client else "unknown"

            # Check rate limit
            is_allowed, remaining = rate_limiter.is_allowed(client_ip)

            if not is_allowed:
                if logger:
                    logger.warning(
                        f"Rate limit exceeded for {client_ip}",
                        extra={
                            'extra_data': {
                                'client_ip': client_ip,
                                'path': request.url.path,
                                'method': request.method
                            }
                        }
                    )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Rate limit exceeded",
                        "limit": settings.RATE_LIMIT_REQUESTS,
                        "window": f"{settings.RATE_LIMIT_WINDOW}s",
                        "retry_after": settings.RATE_LIMIT_WINDOW
                    }
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = f"{settings.RATE_LIMIT_WINDOW}s"

            # Periodic cleanup (every 100 requests)
            self.cleanup_counter += 1
            if self.cleanup_counter >= 100:
                rate_limiter.cleanup_expired()
                self.cleanup_counter = 0

            return response

    return RateLimitMiddleware


# Backward compatibility - export base class
# For users who want to instantiate manually
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    DEPRECATED: Use create_rate_limit_middleware(settings) instead

    This class is kept for backward compatibility but requires
    manual configuration of rate_limiter.
    """
    pass
