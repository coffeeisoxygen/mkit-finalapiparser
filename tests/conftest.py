import asyncio
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from app.config import get_settings
from app.crud.repositories.lite_repo_auditlog import LiteAuditLogRepo
from app.crud.repositories.lite_repo_user import LiteUserRepo
from app.database import DatabaseSessionManager, create_tables, sessionmanager
from app.models import Base
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

PATHTOTESTENV = Path(__file__).parent.parent / ".env.test"


@pytest.fixture(scope="session")
def test_sessionmanager():
    return sessionmanager


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    load_dotenv(dotenv_path=PATHTOTESTENV, override=True)
    get_settings.cache_clear()
    settings = get_settings()

    logger.info(f"[conftest] DB path: {settings.DB_URL}")
    logger.info(f"[conftest] CWD: {os.getcwd()}")
    assert settings.APP_ENV == "TESTING"
    # Re-init sessionmanager for test DB
    global sessionmanager
    sessionmanager = DatabaseSessionManager(settings.DB_URL)
    logger.info(f"Engine id after re-init: {id(sessionmanager.engine)}")

    asyncio.get_event_loop().run_until_complete(create_tables(sessionmanager.engine))


# --- Database tables ---
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    yield
    if sessionmanager.engine is not None:
        async with sessionmanager.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn))


def test_print_sessionmanager(test_sessionmanager):
    print("SessionManager:", test_sessionmanager)
    print("Engine:", test_sessionmanager.engine)
    assert test_sessionmanager.engine is not None


@pytest.fixture
async def test_db_session():
    async with sessionmanager.session() as session:
        yield session


@pytest.mark.asyncio
async def test_print_db_session(test_db_session):
    print("AsyncSession:", test_db_session)
    assert test_db_session is not None


# ==================== EVENT LOOP ====================
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==================== REPOSITORY FIXTURES ====================
@pytest.fixture
def user_repository(async_session: AsyncSession) -> LiteUserRepo:
    """LiteUserRepo instance untuk testing."""
    return LiteUserRepo(async_session)


@pytest.fixture
def auditlog_repository(async_session: AsyncSession) -> LiteAuditLogRepo:
    """LiteAuditLogRepo instance untuk testing."""
    return LiteAuditLogRepo(async_session)
