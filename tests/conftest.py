from pathlib import Path

import pytest
import yaml
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
    assert settings.app_env == "TESTING", (
        f"Expected app_env=TESTING but got {settings.app_env}"
    )

    print(f"Test env loaded app_env={settings.app_env}")


# --- INSTRUKSI SETUP FIXTURE DATA ---
# Pastikan folder 'tests/data' sudah dibuat dan file YAML seperti 'members_valid.yaml' tersedia di sana.
# Contoh: tests/data/members_valid.yaml


@pytest.fixture(scope="session")
def test_file_path():
    """Fixture untuk memberikan path ke folder data test secara robust."""
    # Path selalu relatif terhadap root project
    return Path(__file__).parent.resolve() / "data"


@pytest.fixture(scope="session")
def valid_members_data(test_file_path):
    """Fixture untuk memuat data member valid dari YAML."""
    yaml_path = test_file_path / "members_valid.yaml"
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["members"]
