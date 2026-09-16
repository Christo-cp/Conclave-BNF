"""Application settings (plan A2).

`ENV_FILE` selects the env file, default `.env`; a relative path is resolved against
the project root. Real environment variables override the file.
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def env_file_path() -> Path:
    path = Path(os.environ.get("ENV_FILE", ".env"))
    return path if path.is_absolute() else PROJECT_ROOT / path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/smart_ambulance_dev"
    jwt_secret: str = "development-only-change-me-32-byte-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    simulation_enabled: bool = True
    resource_stale_after_s: int = 300
    gps_stale_after_s: int = 60
    reservation_hold_ttl_s: int = 60
    eta_cap_s: int = 3600
    reroute_significant_delta_s: int = 120
    routing_provider: str = "mock"
    config_version: str = "mvp-1"


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=env_file_path(), _env_file_encoding="utf-8")
