# app/deps/deps_security.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.deps.deps_auth import get_auth_service
from app.schemas.sch_user import User
from app.service.auth.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_current_user(  # noqa: RUF029
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    """Retrieve the current user from the JWT token.

    Args:
        token (str): JWT token from Authorization header.
        auth (AuthService): AuthService facade.

    Returns:
        User: User object from token.

    Raises:
        HTTPException: If token is invalid, expired, or user not found.
    """
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
    """Ensure the current user is active (not disabled).

    Args:
        current_user (User): User object from `get_current_user`.

    Returns:
        User: Active user.

    Raises:
        HTTPException: If user.disabled is True.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Annotated dependencies for FastAPI router injection
DepCurrentUser = Annotated[User, Depends(get_current_active_user)]
DepRawUser = Annotated[User, Depends(get_current_user)]
