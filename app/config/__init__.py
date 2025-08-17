"""project environments configurations."""

from enum import StrEnum
from typing import TYPE_CHECKING

from app._version import version

if TYPE_CHECKING:
    from app._version import __version__ as version

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_ENV_FILE = BASE_DIR / ".env"


class EnvironmentEnums(StrEnum):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"


class ProviderEnums(StrEnum):
    DIGIPOS = "DIGIPOS"
    ISIMPLE = "ISIMPLE"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: EnvironmentEnums = EnvironmentEnums.PRODUCTION
    app_debug: bool = False
    app_name: str = "MKIT_WRAPPER"
    app_version: str = version
    db_path: str
    config_path: str


@lru_cache
def get_settings(_env_file: str | Path | None = None) -> Settings:
    """Prioritas:.

    1. Argumen _env_file
    2. ENV_FILE dari environment variable
    3. DEFAULT_ENV_FILE (.env)
    """
    env_file = _env_file or os.getenv("ENV_FILE", DEFAULT_ENV_FILE)
    return Settings(_env_file=env_file, _env_file_encoding="utf-8")  # type: ignore
