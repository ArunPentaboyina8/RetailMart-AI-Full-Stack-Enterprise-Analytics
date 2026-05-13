# =============================================================================
# RetailMart AI Analytics Platform - Configuration
# =============================================================================
"""
Centralized configuration using Pydantic Settings.
Reads from .env file and provides type-safe config access.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # --- App ---
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    debug: bool = True

    # --- Database ---
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "retailmart"
    db_user: str = "postgres"
    db_password: str = "postgres"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # --- Gemini ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"

    # --- AI ---
    max_tokens: int = 2000
    temperature: float = 0.1
    cache_ttl_seconds: int = 300
    max_sql_complexity: int = 5
    enable_fallback: bool = True
    fallback_model: str = "gemini-2.5-flash"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "retailmart_knowledge"

    # --- Monitoring ---
    enable_cost_tracking: bool = True
    max_daily_cost_usd: float = 5.00

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once."""
    return Settings()
