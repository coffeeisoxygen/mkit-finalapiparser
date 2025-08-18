"""register all routers."""

from fastapi import Depends

from app.api.v1 import member_router, module_router, user_router
from app.deps.security import get_current_user


def register_routers(app):  # noqa: ANN001
    """Register all API routers.

    This function registers all API routers to the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.include_router(
        member_router,
        prefix="/api/v1/member",
        tags=["Member"],
        dependencies=[Depends(get_current_user)],
    )
    app.include_router(
        module_router,
        prefix="/api/v1/module",
        tags=["Module"],
        dependencies=[Depends(get_current_user)],
    )
    app.include_router(
        user_router,
        prefix="/api/v1/user",
        tags=["User"],
    )
