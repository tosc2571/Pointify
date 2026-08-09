from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET_KEY = "dev-only-insecure-secret-key"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = _DEV_SECRET_KEY
    database_url: str = "sqlite:///./pointify.db"

    def validate_secret_key(self) -> None:
        if self.environment != "development" and self.secret_key == _DEV_SECRET_KEY:
            raise RuntimeError("SECRET_KEY must be set via environment variable outside of development")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_secret_key()
    return settings
