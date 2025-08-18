from fastapi.concurrency import asynccontextmanager

from app.mlogg import init_logging, logger
from app.repositories.rep_member import SyncInmemoryMemberRepo
from app.repositories.rep_module import SyncInmemoryModuleRepo
from app.repositories.rep_user import UserRepository


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, RUF029
    """Lifespan context manager for the FastAPI application."""
    try:
        init_logging()
        logger.info("Application starting up")
        # Initialize repositories and attach to app.state
        with logger.contextualize(repo="member_repo"):
            app.state.member_repo = SyncInmemoryMemberRepo()
            logger.info("Member repository initialized")
        with logger.contextualize(repo="module_repo"):
            app.state.module_repo = SyncInmemoryModuleRepo()
            logger.info("Module repository initialized")
        with logger.contextualize(repo="auth_repo"):
            app.state.auth_repo = UserRepository()
            logger.info("User repository initialized")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    yield
    # cleanup
    try:
        app.state.member_repo = None
        app.state.module_repo = None
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")
        raise
