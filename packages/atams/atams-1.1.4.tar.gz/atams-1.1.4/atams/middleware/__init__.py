"""
Middleware
=========
FastAPI middleware for request tracking and rate limiting.

Usage in user project:
    from atams.middleware import RequestIDMiddleware, create_rate_limit_middleware
    from app.core.config import settings

    app.add_middleware(create_rate_limit_middleware(settings))
    app.add_middleware(RequestIDMiddleware)
"""
from atams.middleware.request_id import RequestIDMiddleware
from atams.middleware.rate_limiter import RateLimitMiddleware, create_rate_limit_middleware

__all__ = [
    "RequestIDMiddleware",
    "RateLimitMiddleware",
    "create_rate_limit_middleware",
]
