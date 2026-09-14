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

    app_env: str
    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=env_file_path(), _env_file_encoding="utf-8")
