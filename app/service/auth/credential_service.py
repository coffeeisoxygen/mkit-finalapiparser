# app/service/auth/credential_service.py
from app.custom.exceptions.cst_exceptions import UserNotFoundError, UserPasswordError
from app.mlogg import logger
from app.repositories.memory.rep_user import UserRepository
from app.schemas.sch_user import UserInDB
from app.service.security.srv_hasher import HasherService


class CredentialService:
    """Verifikasi kredensial username + password."""

    def __init__(self, user_repo: UserRepository, hasher: HasherService):
        self.user_repo = user_repo
        self.hasher = hasher
        logger.bind(service="CredentialService").debug("CredentialService initialized")

    def authenticate(self, username: str, password: str) -> UserInDB | None:
        user = self.user_repo.get(username)
        if not user:
            logger.bind(service="CredentialService").warning(
                "User not found", username=username
            )
            raise UserNotFoundError()
        if not self.hasher.verify_value(password, user.hashed_password):
            logger.bind(service="CredentialService").warning(
                "Incorrect password", username=username
            )
            raise UserPasswordError()
        logger.bind(service="CredentialService").info(
            "User authenticated successfully", username=username
        )
        return user
