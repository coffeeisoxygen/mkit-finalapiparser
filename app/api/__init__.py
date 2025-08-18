from fastapi import Depends

from app.api.v1 import member_router, module_router, user_router
from app.deps.security import get_current_user
from app.mlogg import logger


def register_routers(app):  # noqa: ANN001
    """Register all API routers to the FastAPI app."""
    app.include_router(member_router, dependencies=[Depends(get_current_user)])
    app.include_router(module_router, dependencies=[Depends(get_current_user)])
    app.include_router(user_router)
    logger.info("Routers registered successfully")
