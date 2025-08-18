# app/deps/deps_security.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.deps.deps_auth import get_auth_service
from app.schemas.sch_user import User
from app.service.auth.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_current_user(  # noqa: RUF029
    token: str = Depends(oauth2_scheme), auth: AuthService = Depends(get_auth_service)
) -> User:
    """Get the current user from the token."""
    try:
        return auth.get_user_from_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(  # noqa: RUF029
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Annotated dependencies for cleaner router injection


DepCurrentUser = Annotated[User, Depends(get_current_active_user)]
DepRawUser = Annotated[User, Depends(get_current_user)]
