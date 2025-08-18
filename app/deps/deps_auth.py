# app/deps/deps_auth.py
from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.deps.deps_service import get_user_repo
from app.repositories.rep_user import UserRepository
from app.service.auth.auth_service import AuthService
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService
from app.service.security.srv_hasher import HasherService

settings = get_settings()
hasher_service = HasherService()


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    """Provide a fully initialized AuthService for dependency injection.

    Args:
        user_repo (UserRepository): Repository to access user data.

    Returns:
        AuthService: Facade for login and token handling.
    """
    # Sub-services
    cred_service = CredentialService(user_repo=user_repo, hasher=hasher_service)
    token_service = TokenService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    # AuthService facade
    return AuthService(
        credential_service=cred_service,
        token_service=token_service,
        user_repo=user_repo,
    )


# Annotated dependency for FastAPI endpoints
DepAuthService: Annotated[AuthService, Depends(get_auth_service)]
