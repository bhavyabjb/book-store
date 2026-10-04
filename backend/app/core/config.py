from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/bookworm"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5433/bookworm"

    JWT_SECRET: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost"

    # Base URL the browser can reach this API at, used to build absolute
    # URLs for server-generated static assets (e.g. placeholder cover art).
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
