from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.service.auth_service import AuthService
from app.service.srv_hasher import HasherService


def get_hasher() -> HasherService:  # noqa: D103
    return HasherService()


def get_auth_service(  # noqa: D103
    settings=Depends(get_settings),
    hasher=Depends(get_hasher),  # noqa: ANN001
) -> AuthService:
    return AuthService(settings=settings, hasher=hasher)


# Annotated shortcut
DepAuthService = Annotated[AuthService, Depends(get_auth_service)]
