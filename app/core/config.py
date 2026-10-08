import os
from functools import lru_cache
from pathlib import Path
from pydantic import Field, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Core Application Controls
    ENVIRONMENT: str = Field(default="production")
    APP_NAME: str = Field(default="Telemetry System")
    API_V1_STR: str = "/api/v1"
    API_KEY_SECRET: str = Field(default="dev-secret-key")
    
    # 🔥 Multi-driver compatibility allowance for local verification setups
    POSTGRES_DSN: PostgresDsn | MultiHostUrl | str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
