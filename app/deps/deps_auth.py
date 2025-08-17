# deps_auth.py
from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.deps.deps_service import get_user_repo
from app.service.auth_service import AuthService
from app.service.srv_hasher import HasherService

settings = get_settings()
hasher_service = HasherService()


def get_auth_service(
    user_repo=Depends(get_user_repo),
) -> AuthService:
    """Provide AuthService instance for DI."""
    return AuthService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user_repo=user_repo,
        hasher=hasher_service,
    )


DepAuthService = Annotated[AuthService, Depends(get_auth_service)]
