import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.custom.exceptions import ServiceError
from app.mlogg import logger

settings = get_settings()


class DatabaseSessionManager:
    """Manages async database connections and sessions."""

    def __init__(self, db_url: str):
        self.engine: AsyncEngine | None = create_async_engine(db_url, echo=False)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
            async_sessionmaker(self.engine, expire_on_commit=False)
        )
        logger.debug("DatabaseSessionManager initialized")

    async def close(self) -> None:
        """Dispose engine and reset sessionmaker."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self._sessionmaker = None
            logger.debug("Database engine disposed")

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Provide an async connection (non-ORM)."""
        if self.engine is None:
            raise ServiceError("Database engine is not initialized")

        async with self.engine.connect() as connection:
            try:
                yield connection
            except SQLAlchemyError as e:
                await connection.rollback()
                logger.bind(method="connect", db_url=str(self.engine.url)).exception(
                    "Connection error occurred"
                )
                raise ServiceError(message=str(e), cause=e) from e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session with rollback & close handling.

        Caller is responsible for commit.
        """
        if not self._sessionmaker:
            logger.error("Sessionmaker is not available")
            raise ServiceError("Sessionmaker is not available")

        async with self._sessionmaker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                db_url = str(self.engine.url) if self.engine else "N/A"
                logger.bind(method="session", db_url=db_url).exception("Session error")
                raise ServiceError(message=str(e), cause=e) from e
            except Exception as e:
                await session.rollback()
                db_url = str(self.engine.url) if self.engine else "N/A"
                logger.bind(method="session", db_url=db_url).exception(
                    "Unexpected session error"
                )
                raise ServiceError(message=str(e), cause=e) from e
            finally:
                await session.close()


# Singleton instance for FastAPI
sessionmanager = DatabaseSessionManager(settings.DB_URL)


@contextlib.asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency to yield a database session.

    Caller must commit explicitly if needed.
    """
    async with sessionmanager.session() as session:
        yield session
