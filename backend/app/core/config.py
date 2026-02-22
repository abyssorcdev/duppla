import os
from typing import Any, Dict, List

from pydantic_settings import BaseSettings
from fastapi import HTTPException, status


class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be overridden via environment variables.
    Example: POSTGRES_USER=myuser will override the default.

    Managed platforms (Render, Railway, etc.) inject DATABASE_URL and
    REDIS_URL directly.  When present they take precedence over the
    individual host/port/user/password variables.
    """

    PROJECT_NAME: str = "Duppla API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False

    # Database — individual vars for local dev / docker-compose
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"  # noqa: S105
    POSTGRES_DB: str = "duppla"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """Return DATABASE_URL from env if set, otherwise build from components."""
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis — individual vars for local dev / docker-compose
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """Return REDIS_URL from env if set, otherwise build from components."""
        url = os.getenv("REDIS_URL")
        if url:
            return url
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    VALID_API_KEYS: dict = {
        "get": ["get-key-123"],
        "post": ["post-key-456"],
        "put": ["put-key-789"],
        "patch": ["patch-key-012"],
        "delete": ["delete-key-345"],
    }

    def API_KEYS_ALLOWED(self, method: str) -> List[str]:
        """Get the list of API keys allowed for a given HTTP method (GET, POST, PUT, DELETE)."""
        keys = self.VALID_API_KEYS.get(method.lower(), [])
        if not keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No API keys found for this request method.",
            )
        return keys

    NOTIFICATION_CHANNELS: List[Dict[str, Any]] = [
        {
            "type": "http",
            "name": "external_monitoring",
            "url": "https://webhook.site/a68da993-7a22-4521-a267-507e7f94b1ac",
            "headers": {
                "Content-Type": "application/json",
            },
        },
    ]

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Cache & Rate limiting
    API_KEY_CACHE_TTL: int = 300  # seconds — how long a validated key stays cached
    RATE_LIMIT_REQUESTS: int = 100  # max requests per window per API key
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # sliding window size in seconds

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"  # noqa: S105
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Frontend URL (used for OAuth redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
