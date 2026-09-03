from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ULTRON"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    embedding_provider: str = "local"
    stt_provider: str = "disabled"
    tts_provider: str = "disabled"
    web_search_provider: str = "disabled"
    database_url: str = "postgresql+psycopg://ultron:ultron@postgres:5432/ultron"
    redis_url: str = "redis://redis:6379/0"
    vector_db: str = "pgvector"
    emergency_stop: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ULTRON_", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
