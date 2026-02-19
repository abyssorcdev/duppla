from typing import Any, Dict, List

from pydantic_settings import BaseSettings
from fastapi import HTTPException, status


class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be overridden via environment variables.
    Example: POSTGRES_USER=myuser will override the default.
    """

    # Application
    PROJECT_NAME: str = "Duppla API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"  # noqa: S105  # Default value, override with .env
    POSTGRES_DB: str = "duppla"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Celery broker URL (Redis)."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery result backend URL (Redis)."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Security - API Keys
    VALID_API_KEYS: dict = {}

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
    RATE_LIMIT_REQUESTS: int = 10  # max requests per window per API key
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # sliding window size in seconds

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
