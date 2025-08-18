from app.api.v1.rtr_member import router as member_router
from app.api.v1.rtr_module import router as module_router
from app.api.v1.rtr_user import router as user_router

__all__ = ["member_router", "module_router", "user_router"]
