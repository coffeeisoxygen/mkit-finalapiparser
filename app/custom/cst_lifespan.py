from fastapi.concurrency import asynccontextmanager

from app.config import get_settings
from app.deps.deps_service import get_admin_seed_service
from app.mlogg.setup import init_logging, logger

ENV = get_settings().APP_ENV.value


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, ARG001
    """Lifespan context manager for the FastAPI application."""
    init_logging()
    logger.info("Application starting up")
    # Seed admin user
    admin_seed_service = await get_admin_seed_service()
    await admin_seed_service.seed_default_admin()
    yield
    # cleanup
    logger.info("Application shutting down")
