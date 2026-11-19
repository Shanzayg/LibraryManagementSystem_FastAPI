from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads values from the .env file (and from real environment variables).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Library API"
    DEBUG: bool = False

    # Filled in during topic 12 (Neon). Empty is fine until then.
    DATABASE_URL: str = ""

    # No default on purpose: the app refuses to start if SECRET_KEY is missing.
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MAX_LOANS_PER_USER: int = 3
    LOAN_DAYS: int = 14

    # Comma-separated text in .env, e.g. http://localhost:3000,http://127.0.0.1:3000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Create Settings once and reuse it (lru_cache), instead of re-reading .env every time."""
    return Settings()