# app/api/v1/user_router.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.deps.deps_security import DepCurrentUser, get_auth_service
from app.schemas.sch_user import Token, User
from app.service.auth.auth_service import AuthService

router = APIRouter(
    prefix="/api/v1/user",
    tags=["User"],
)


# ---------------------------
# POST /api/v1/user/login
# ---------------------------
@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        }
    },
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login user dan dapatkan JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): username & password dari form.
        auth_service (DepAuthService): DI AuthService facade.

    Returns:
        Token: JWT access token.
    """
    token = auth_service.login(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=token, token_type="bearer")


# ---------------------------
# GET /api/v1/user/me
# ---------------------------
@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: DepCurrentUser,
):
    """Ambil data user yang sedang login dan aktif.

    Args:
        current_user (User): DI dependency, sudah valid login + active check.

    Returns:
        User: data user saat ini.
    """
    return current_user
