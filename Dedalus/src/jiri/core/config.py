"""Application configuration using Pydantic Settings.

Loads configuration from environment variables and .env file.
All settings are type-validated and have sensible defaults for development.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Jiri"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"

    # --- Database (TimescaleDB) ---
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://jiri:jiri_dev_password@localhost:5432/jiri",
        description="Async PostgreSQL connection string",
    )

    # --- Redis ---
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    # --- ChromaDB ---
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # --- API Security ---
    api_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="API key for service-to-service auth",
    )

    # --- Azure Voice Live (Optional) ---
    azure_speech_key: str | None = None
    azure_speech_region: str = "eastus2"

    # --- OpenAI / LLM (Optional) ---
    openai_api_key: str | None = None

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def chroma_url(self) -> str:
        """Get ChromaDB HTTP URL."""
        return f"http://{self.chroma_host}:{self.chroma_port}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()
