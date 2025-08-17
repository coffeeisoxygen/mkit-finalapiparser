from pathlib import Path

import pytest
import yaml
from app.config import get_settings
from app.mlogg import logger
from dotenv import load_dotenv

PATHTOTESTENV = Path(__file__).parent.parent / ".env.test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # Load .env.test ke os.environ, override env vars yang ada
    load_dotenv(dotenv_path=PATHTOTESTENV, override=True)

    get_settings.cache_clear()
    settings = get_settings()  # sekarang ambil dari os.environ yang sudah di-override

    assert PATHTOTESTENV.exists(), f".env.test file not found at {PATHTOTESTENV}"
    assert settings.app_env == "TESTING", (
        f"Expected app_env=TESTING but got {settings.app_env}"
    )

    print(f"Test env loaded app_env={settings.app_env}")


@pytest.fixture(autouse=True)
def intercept_loguru(caplog):
    handler_id = logger.add(
        sink=caplog.handler,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        enqueue=False,
    )
    yield
    logger.remove(handler_id)


# fixture file untuk test
@pytest.fixture(scope="session")
def test_file_path():
    """Fixture untuk memberikan path ke file yang akan di-load dalam test."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def valid_members_data(test_file_path):
    """Fixture untuk memuat data member valid dari YAML."""
    yaml_path = test_file_path / "members_valid.yaml"
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["members"]
