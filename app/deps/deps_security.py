# ruff : noqa:RUF029
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.deps.deps_service import get_auth_service
from app.schemas.sch_token import UserToken
from app.service.auth.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> UserToken:
    """Ambil user dari JWT token."""
    try:
        return auth.get_user_from_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_admin(
    user: UserToken = Depends(get_current_user),
) -> UserToken:
    """Pastikan user adalah admin."""
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


async def get_current_active_user(
    user: UserToken = Depends(get_current_user),
) -> UserToken:
    """Pastikan user aktif."""
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Annotated dependencies for FastAPI router injection
DepCurrentUser = Annotated[UserToken, Depends(get_current_user)]
DepCurrentAdmin = Annotated[UserToken, Depends(get_current_admin)]
DepActiveUser = Annotated[UserToken, Depends(get_current_active_user)]
