# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.deps.deps_auth import Annotated, DepAuthService
from app.schemas.sch_user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_current_user(
    auth: DepAuthService,
    token: str = Depends(oauth2_scheme),
):
    """Retrieve the current user from the JWT token."""
    try:
        user = auth.get_user_from_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


DepCurrentUser = Annotated[User, Depends(get_current_active_user)]
