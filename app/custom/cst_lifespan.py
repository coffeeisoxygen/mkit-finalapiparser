from fastapi.concurrency import asynccontextmanager

from app.config import get_settings
from app.mlogg.setup import init_logging, logger

ENV = get_settings().APP_ENV.value


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, ARG001, RUF029
    """Lifespan context manager for the FastAPI application."""
    init_logging()
    logger.info("Application starting up")
    yield
    # cleanup
    logger.error("Error during application shutdown:")
