from pathlib import Path

import pytest
from app.config import get_settings
from dotenv import load_dotenv

PATHTOTESTENV = Path(__file__).parent.parent / ".env.test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # Load .env.test ke os.environ, override env vars yang ada
    load_dotenv(dotenv_path=PATHTOTESTENV, override=True)

    get_settings.cache_clear()
    settings = get_settings()  # sekarang ambil dari os.environ yang sudah di-override

    assert PATHTOTESTENV.exists(), f".env.test file not found at {PATHTOTESTENV}"
    assert settings.APP_ENV == "TESTING", (
        f"Expected APP_ENV=TESTING but got {settings.APP_ENV}"
    )

    print(f"Test env loaded app_env={settings.APP_ENV}")
