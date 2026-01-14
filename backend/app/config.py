"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "TranscripTok"
    app_env: Literal["development", "production", "testing"] = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # API
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/transcriptok"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Whisper
    whisper_mode: Literal["local", "api"] = "local"
    whisper_model: str = "base"  # tiny, base, small, medium, large

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None

    # Storage
    storage_type: Literal["local", "s3"] = "local"
    storage_path: str = "./storage"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
