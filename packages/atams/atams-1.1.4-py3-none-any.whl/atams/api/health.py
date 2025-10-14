"""
Health Check Endpoints
======================
Built-in health check endpoints for monitoring database and application status

Usage in user project:
    from fastapi import FastAPI
    from atams.api import health_router

    app = FastAPI()
    app.include_router(health_router, prefix="/health", tags=["Health"])

This provides:
    GET /health - Basic health check
    GET /health/db - Database health with connection pool status
    GET /health/full - Full health check (app + database)
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def basic_health() -> Dict[str, Any]:
    """
    Basic health check endpoint

    Returns:
        Simple status indicating the application is running

    Example Response:
        {
            "status": "ok",
            "timestamp": "2025-01-13T10:00:00"
        }
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/db", status_code=status.HTTP_200_OK)
async def database_health() -> JSONResponse:
    """
    Database health check with connection pool status

    Checks:
    - Database connectivity
    - Connection pool statistics
    - Connection health

    Returns:
        JSON response with database health status and pool metrics

    Example Response (Healthy):
        {
            "status": "ok",
            "database": {
                "connected": true,
                "pool": {
                    "pool_size": 3,
                    "checked_in": 2,
                    "checked_out": 1,
                    "overflow": 0,
                    "total_connections": 3
                }
            },
            "timestamp": "2025-01-13T10:00:00"
        }

    Example Response (Unhealthy):
        {
            "status": "error",
            "database": {
                "connected": false,
                "error": "Connection timeout"
            },
            "timestamp": "2025-01-13T10:00:00"
        }
    """
    try:
        from atams.db import check_connection_health, get_pool_status

        is_healthy = check_connection_health()

        if not is_healthy:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "error",
                    "database": {
                        "connected": False,
                        "error": "Database connection failed"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        # Get pool status
        pool_status = get_pool_status()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "database": {
                    "connected": True,
                    "pool": pool_status
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except RuntimeError as e:
        # Database not initialized
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": {
                    "connected": False,
                    "error": str(e)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": {
                    "connected": False,
                    "error": f"Unexpected error: {str(e)}"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/full", status_code=status.HTTP_200_OK)
async def full_health() -> JSONResponse:
    """
    Full health check including application and database

    Performs comprehensive health checks:
    - Application status
    - Database connectivity
    - Connection pool metrics

    Returns:
        JSON response with full system health status

    Example Response:
        {
            "status": "ok",
            "application": {
                "status": "running",
                "timestamp": "2025-01-13T10:00:00"
            },
            "database": {
                "connected": true,
                "pool": {...}
            }
        }
    """
    response_data = {
        "application": {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    # Check database health
    try:
        from atams.db import check_connection_health, get_pool_status

        is_healthy = check_connection_health()

        if is_healthy:
            pool_status = get_pool_status()
            response_data["database"] = {
                "connected": True,
                "pool": pool_status
            }
            response_data["status"] = "ok"
            status_code = status.HTTP_200_OK
        else:
            response_data["database"] = {
                "connected": False,
                "error": "Database connection failed"
            }
            response_data["status"] = "degraded"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    except RuntimeError as e:
        # Database not initialized - optional component
        response_data["database"] = {
            "connected": False,
            "error": str(e),
            "note": "Database is not initialized. This is optional."
        }
        response_data["status"] = "ok"  # App is still running
        status_code = status.HTTP_200_OK
    except Exception as e:
        response_data["database"] = {
            "connected": False,
            "error": f"Unexpected error: {str(e)}"
        }
        response_data["status"] = "degraded"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )
