"""
ATAMS API Module
================
Provides built-in API endpoints for health checks and monitoring
"""
from atams.api.health import router as health_router

__all__ = ["health_router"]
