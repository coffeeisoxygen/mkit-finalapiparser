from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency to yield a database session.

    Caller must commit explicitly if needed.
    """
    async with sessionmanager.session() as session:
        yield session