"""Admin router: user CRUD, hanya bisa diakses admin."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps.deps_security import DepCurrentAdmin
from app.deps.deps_service import get_user_crud_service
from app.schemas.sch_user import UserCreate, UserResponse
from app.service.user import UserCrudService

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.post("/user", response_model=UserResponse, status_code=201)
async def create_user_by_admin(
    user_in: Annotated[UserCreate, Depends()],
    current_admin: DepCurrentAdmin,
    user_crud: Annotated[UserCrudService, Depends(get_user_crud_service)],
):
    """Admin create user (pendaftaran user baru).

    Args:
            user_in (UserCreate): Data user baru.
            current_admin (UserToken): DI, sudah valid admin.
            user_crud (UserCrudService): DI, service CRUD user.

    Returns:
            UserResponse: Data user yang baru dibuat.
    """
    try:
        user = await user_crud.create_user(user_in, actor_id=current_admin.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    else:
        return user
