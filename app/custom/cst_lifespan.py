from fastapi.concurrency import asynccontextmanager

from mlogg import init_logging, logger


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, ARG001, RUF029
    """Lifespan context manager for the FastAPI application."""
    try:
        init_logging()
        logger.info("Application starting up")

    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    yield

    logger.error("Error during application shutdown: ")
