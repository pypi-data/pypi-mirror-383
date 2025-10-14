from pydantic_settings import BaseSettings
from typing import List
import json


class AtamsBaseSettings(BaseSettings):
    """
    Base settings untuk semua AURA applications
    Inherit class ini di project-specific settings
    """

    # Database (required per app)
    DATABASE_URL: str

    # Database Connection Pool Settings
    # IMPORTANT: Tune these based on your database connection limit!
    # For Aiven free tier (20 connections), use smaller values:
    #   DB_POOL_SIZE=3, DB_MAX_OVERFLOW=5 (max 8 per app)
    # For production with higher limits, increase accordingly
    DB_POOL_SIZE: int = 3  # Number of persistent connections
    DB_MAX_OVERFLOW: int = 5  # Additional connections when pool is full
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour (prevent stale connections)
    DB_POOL_TIMEOUT: int = 30  # Timeout waiting for connection (seconds)
    DB_POOL_PRE_PING: bool = True  # Verify connection health before using

    # Atlas SSO Configuration
    # All configurable via .env untuk development flexibility
    ATLAS_SSO_URL: str = "https://api.atlas-microapi.atamsindonesia.com/api/v1"
    ATLAS_APP_CODE: str
    ATLAS_ENCRYPTION_KEY: str = "7c5f7132ba1a6e566bccc56416039bea"
    ATLAS_ENCRYPTION_IV: str = "ce84582d0e6d2591"

    # Response Encryption (app-specific)
    ENCRYPTION_ENABLED: bool = False
    ENCRYPTION_KEY: str = "change_me_32_characters_long!!"  # Must be 32 chars
    ENCRYPTION_IV: str = "change_me_16char"  # Must be 16 chars

    # Logging (common pattern dengan defaults)
    LOGGING_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/app.log"

    # Debug mode
    DEBUG: bool = False

    # CORS Configuration (dengan default ATAMS ecosystem)
    CORS_ORIGINS: str = '["*"]'
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = '["*"]'
    CORS_ALLOW_HEADERS: str = '["*"]'

    # Rate Limiting (common pattern dengan defaults)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS_ORIGINS dengan default ATAMS security

        DEFAULT: Hanya *.atamsindonesia.com + localhost dev
        """
        try:
            origins = json.loads(self.CORS_ORIGINS)

            # Jika ["*"], apply default ATAMS security
            if origins == ["*"]:
                return [
                    "https://*.atamsindonesia.com",
                    "http://localhost:3000",
                    "http://localhost:8000",
                ]

            return origins
        except:
            return [
                "https://*.atamsindonesia.com",
                "http://localhost:3000",
                "http://localhost:8000",
            ]

    @property
    def cors_methods_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ALLOW_METHODS)
        except:
            return ["*"]

    @property
    def cors_headers_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ALLOW_HEADERS)
        except:
            return ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_database_url():
    """Helper untuk get DATABASE_URL dari environment"""
    from os import getenv
    db_url = getenv("DATABASE_URL", "")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    return db_url
