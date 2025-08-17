"""register all routers."""

from app.api.v1.member.rtr_member import router as member_router


def register_routers(app):
    app.include_router(member_router, prefix="/api/v1", tags=["Member"])
