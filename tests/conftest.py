import asyncio
import os
from pathlib import Path

import app.database.session as db_session
import pytest
from app.config import get_settings
from app.database.session import sessionmanager
from app.database.table import create_tables
from app.models import Base
from dotenv import load_dotenv
from loguru import logger

PATHTOTESTENV = Path(__file__).parent.parent / ".env.test"


# --- SessionManager Fixture ---
@pytest.fixture(scope="session")
def test_sessionmanager():
    return sessionmanager


# --- Environment ---
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    load_dotenv(dotenv_path=PATHTOTESTENV, override=True)
    get_settings.cache_clear()
    settings = get_settings()

    logger.info(f"[conftest] DB path: {settings.DB_URL}")
    logger.info(f"[conftest] CWD: {os.getcwd()}")
    assert settings.APP_ENV == "TESTING"
    db_session.sessionmanager = db_session.DatabaseSessionManager(settings.DB_URL)
    logger.info(f"Engine id after re-init: {id(db_session.sessionmanager.engine)}")

    asyncio.get_event_loop().run_until_complete(
        create_tables(db_session.sessionmanager.engine)
    )


# --- Database tables ---
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    yield
    if db_session.sessionmanager.engine is not None:
        async with db_session.sessionmanager.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn))
