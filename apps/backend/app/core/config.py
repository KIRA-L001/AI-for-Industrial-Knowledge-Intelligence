"""Application configuration loaded from environment variables.

Single typed settings object (`get_settings`) used across the app via DI.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings sourced from the environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- General ---
    kira_env: Literal["development", "staging", "production", "test"] = "development"
    log_level: str = "INFO"
    project_name: str = "KIRA"
    api_v1_prefix: str = "/api/v1"
    # Dev affordance: create all tables on startup (use with SQLite for local
    # runs without Docker/Alembic). Never enable in production.
    auto_create_db: bool = False

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # --- Auth ---
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- PostgreSQL ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "kira"
    postgres_password: str = "kira_password"
    postgres_db: str = "kira"
    database_url: str | None = None

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "kira_neo4j_password"

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "kira_chunks"

    # --- MinIO ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "kira"
    minio_secret_key: str = "kira_minio_password"
    minio_bucket: str = "kira-documents"
    minio_secure: bool = False

    # --- AI / LLM ---
    llm_provider: Literal["anthropic", "openai", "ollama", "none"] = "none"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Async SQLAlchemy connection string."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins parsed into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.kira_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
