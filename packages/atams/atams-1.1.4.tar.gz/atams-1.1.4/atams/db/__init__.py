"""
Database Layer
==============
Provides database session management and base repository pattern.

Usage:
    from atams.db import Base, get_db, BaseRepository, init_database

Connection Pool Monitoring:
    from atams.db import get_pool_status, check_connection_health
"""
from atams.db.base import Base
from atams.db.session import (
    SessionLocal,
    engine,
    get_db,
    init_database,
    get_pool_status,
    dispose_pool,
    check_connection_health,
    get_connection_url_info,
)
from atams.db.repository import BaseRepository

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "init_database",
    "BaseRepository",
    # Connection pool utilities
    "get_pool_status",
    "dispose_pool",
    "check_connection_health",
    "get_connection_url_info",
]
