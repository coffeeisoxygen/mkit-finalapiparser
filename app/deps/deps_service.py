"""dependencies untuk service service."""

from app.config import get_settings
from app.database import get_db_session
from app.service.auth.auth_service import AuthService
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService
from app.service.user import AdminSeedService, UserCrudService

settings = get_settings()


async def get_user_crud_service() -> UserCrudService:
    """Get User CRUD Service.

    This function provides a User CRUD Service instance.

    Returns:
        UserCrudService: An instance of UserCrudService
    """
    async with get_db_session() as session:
        return UserCrudService(session)


async def get_admin_seed_service() -> AdminSeedService:
    """Get Admin Seed Service.

    This function provides an Admin Seed Service instance.

    Returns:
        AdminSeedService: An instance of AdminSeedService
    """
    async with get_db_session() as session:
        return AdminSeedService(session)


async def get_auth_service() -> AuthService:
    """Get Auth Service.

    This function provides an Auth Service instance.

    Returns:
        AuthService: An instance of AuthService
    """
    async with get_db_session() as session:
        token_service = TokenService(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        credential_service = CredentialService(session)
        return AuthService(credential_service, token_service)
