# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.deps.deps_auth import DepAuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth: DepAuthService = Depends(),
):
    try:
        user = auth.get_user_from_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
