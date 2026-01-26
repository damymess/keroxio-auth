from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Auth service configuration."""

    # Service
    SERVICE_NAME: str = "auth-service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS - Configure for production
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:19006"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from string to list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
