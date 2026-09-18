import os
from pathlib import Path
from functools import lru_cache
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically locate the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="production")
    APP_NAME: str = Field(default="Telemetry System")
    API_V1_STR: str = "/api/v1"
    POSTGRES_DSN: PostgresDsn

    model_config = SettingsConfigDict(
        # Compute the explicit absolute path to the .env file in the project root
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
