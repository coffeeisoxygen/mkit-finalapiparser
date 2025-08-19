from sqlalchemy.ext.asyncio import AsyncSession

from app.custom.exceptions.cst_exceptions import UserNotFoundError, UserPasswordError
from app.database.repositories.repo_user import SQLiteUserRepository
from app.mlogg import logger
from app.schemas.sch_token import UserPasswordToken
from app.service.security.srv_hasher import HasherService


class CredentialService:
    """Service untuk verifikasi kredensial username dan password.

    Pattern: service -> repo -> DB (async).
    """

    def __init__(self, session: AsyncSession, hasher: HasherService | None = None):
        """Inisialisasi CredentialService dengan dependency session dan hasher.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            hasher (HasherService, optional): Service untuk hash/verify password.
        """
        self.session = session
        self.hasher = hasher or HasherService()
        self.log = logger.bind(service="CredentialService")

    async def authenticate(self, username: str, password: str) -> UserPasswordToken:
        """Autentikasi user berdasarkan username dan password.

        Args:
            username (str): Username user.
            password (str): Password plain user.

        Returns:
            UserPasswordToken: Schema berisi hashed_password jika sukses.

        Raises:
            UserNotFoundError: Jika user tidak ditemukan.
            UserPasswordError: Jika password salah.
        """
        repo = SQLiteUserRepository(self.session)
        user = await repo.get_by_username(username)
        if not user:
            self.log.warning("User not found", username=username)
            raise UserNotFoundError("User not found.")
        if not self.hasher.verify_value(password, user.hashed_password):
            self.log.warning("Incorrect password", username=username)
            raise UserPasswordError("Incorrect password.")
        self.log.info("User authenticated successfully", username=username)
        return UserPasswordToken(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            hashed_password=user.hashed_password,
        )
