"""for creating tables."""

from sqlalchemy import inspect

from app.mlogg import logger
from app.models import Base


# Create tables helper
async def create_tables(engine):  # noqa: ANN001
    """Create all database tables.

    This function creates all tables defined in the SQLAlchemy models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True)
        )
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        logger.info(f"Tables after create_tables: {tables}")
