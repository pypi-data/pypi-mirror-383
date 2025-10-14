"""
Database Session Management
===========================
Provides database engine, session factory, and get_db dependency.

Usage in user project:
    # In app/db/session.py (user project)
    from atams.db.session import create_session_factory, get_db_factory
    from app.core.config import settings

    SessionLocal = create_session_factory(settings)
    get_db = get_db_factory(SessionLocal)

Or simpler with init_database:
    # In app/main.py
    from atams.db import init_database
    from app.core.config import settings

    init_database(settings.DATABASE_URL, settings.DEBUG)
"""
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from atams.config.base import AtamsBaseSettings


def normalize_database_url(db_url: str) -> str:
    """
    Normalize database URL (postgres:// -> postgresql+psycopg2://)

    Args:
        db_url: Original database URL

    Returns:
        Normalized database URL
    """
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    return db_url


def create_engine_from_settings(settings: 'AtamsBaseSettings') -> Engine:
    """
    Create SQLAlchemy engine from settings with configurable connection pool

    Connection pool settings are now configurable via environment variables:
    - DB_POOL_SIZE: Number of persistent connections (default: 3)
    - DB_MAX_OVERFLOW: Additional connections when pool is full (default: 5)
    - DB_POOL_RECYCLE: Recycle connections after N seconds (default: 3600)
    - DB_POOL_TIMEOUT: Timeout waiting for connection in seconds (default: 30)
    - DB_POOL_PRE_PING: Verify connection health before using (default: True)

    Args:
        settings: Application settings

    Returns:
        SQLAlchemy engine

    Example .env for Aiven free tier (20 connection limit):
        DB_POOL_SIZE=3
        DB_MAX_OVERFLOW=5
        # This allows max 8 connections per app instance
    """
    db_url = normalize_database_url(settings.DATABASE_URL)

    return create_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        echo=settings.DEBUG,
    )


def create_session_factory(settings: 'AtamsBaseSettings'):
    """
    Create session factory from settings

    Args:
        settings: Application settings

    Returns:
        SessionLocal factory
    """
    engine = create_engine_from_settings(settings)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_factory(session_factory) -> Callable:
    """
    Create get_db dependency function

    Args:
        session_factory: SessionLocal factory

    Returns:
        get_db function
    """
    def get_db() -> Generator[Session, None, None]:
        """Dependency to get database session"""
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    return get_db


# Global variables (will be initialized by init_database)
engine: Engine = None
SessionLocal = None


def init_database(
    database_url: str,
    debug: bool = False,
    pool_size: int = 3,
    max_overflow: int = 5,
    pool_recycle: int = 3600,
    pool_timeout: int = 30,
    pool_pre_ping: bool = True
) -> None:
    """
    Initialize database engine and session factory with configurable connection pool

    This is the main function to call in user projects.

    IMPORTANT: Tune pool settings based on your database connection limit!

    Connection Pool Parameters:
    - pool_size: Number of persistent connections (default: 3)
    - max_overflow: Additional connections when pool is full (default: 5)
    - pool_recycle: Recycle connections after N seconds (default: 3600)
    - pool_timeout: Timeout waiting for connection in seconds (default: 30)
    - pool_pre_ping: Verify connection health before using (default: True)

    Args:
        database_url: Database connection URL
        debug: Enable SQL echo
        pool_size: Number of persistent connections in the pool
        max_overflow: Max additional connections beyond pool_size
        pool_recycle: Seconds before recycling connections
        pool_timeout: Seconds to wait for available connection
        pool_pre_ping: Test connection health before using

    Example (basic):
        from atams.db import init_database
        from app.core.config import settings

        init_database(settings.DATABASE_URL, settings.DEBUG)

    Example (custom pool for Aiven free tier):
        init_database(
            settings.DATABASE_URL,
            settings.DEBUG,
            pool_size=3,
            max_overflow=5
        )

    Example (using settings object):
        init_database(
            settings.DATABASE_URL,
            settings.DEBUG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=settings.DB_POOL_PRE_PING
        )
    """
    global engine, SessionLocal

    db_url = normalize_database_url(database_url)

    engine = create_engine(
        db_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        pool_timeout=pool_timeout,
        pool_pre_ping=pool_pre_ping,
        echo=debug,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session

    Must call init_database() first!

    Example:
        from fastapi import Depends
        from atams.db import get_db

        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    if SessionLocal is None:
        raise RuntimeError(
            "Database not initialized! Call init_database() first in your main.py"
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== CONNECTION POOL UTILITIES ====================


def get_pool_status() -> dict:
    """
    Get current connection pool status for monitoring

    Returns:
        Dictionary with pool statistics:
        - pool_size: Configured pool size
        - checked_in: Connections currently in the pool
        - checked_out: Connections currently in use
        - overflow: Current overflow connections
        - total_connections: Total active connections

    Example:
        from atams.db import get_pool_status

        status = get_pool_status()
        print(f"Active connections: {status['checked_out']}/{status['pool_size']}")

    Raises:
        RuntimeError: If database not initialized
    """
    if engine is None:
        raise RuntimeError("Database not initialized! Call init_database() first")

    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.checkedout() + pool.checkedin(),
    }


def dispose_pool() -> None:
    """
    Dispose all connections in the pool

    Useful for:
    - Cleaning up connections during shutdown
    - Resetting connections after configuration changes
    - Troubleshooting connection issues

    Example:
        from atams.db import dispose_pool

        # On application shutdown
        dispose_pool()

    Raises:
        RuntimeError: If database not initialized
    """
    if engine is None:
        raise RuntimeError("Database not initialized! Call init_database() first")

    engine.dispose()


def check_connection_health() -> bool:
    """
    Check if database connection is healthy

    Returns:
        True if connection is healthy, False otherwise

    Example:
        from atams.db import check_connection_health

        if not check_connection_health():
            print("Database connection unhealthy!")

    Raises:
        RuntimeError: If database not initialized
    """
    if engine is None:
        raise RuntimeError("Database not initialized! Call init_database() first")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_connection_url_info() -> dict:
    """
    Get sanitized database connection info (without password)

    Returns:
        Dictionary with connection information:
        - driver: Database driver (e.g., postgresql+psycopg2)
        - host: Database host
        - port: Database port
        - database: Database name
        - username: Database username

    Example:
        from atams.db import get_connection_url_info

        info = get_connection_url_info()
        print(f"Connected to {info['database']} at {info['host']}")

    Raises:
        RuntimeError: If database not initialized
    """
    if engine is None:
        raise RuntimeError("Database not initialized! Call init_database() first")

    url = engine.url
    return {
        "driver": url.drivername,
        "host": url.host,
        "port": url.port,
        "database": url.database,
        "username": url.username,
        # Note: password is intentionally excluded for security
    }
