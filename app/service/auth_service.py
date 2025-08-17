from app.config import get_settings
from app.custom.cst_exceptions import AuthError
from app.schemas.schuser import UserLogin
from app.service.srv_hasher import HasherService
from mlogg import logger

settings = get_settings()
hasher = HasherService()


class AuthService:
    def login(self, data: UserLogin) -> bool:
        if data.username != settings.app_admin_username:
            logger.error("Invalid username", username=data.username)
            raise AuthError(
                "Invalid username.",
                context={"username": data.username, "reason": "username_mismatch"},
            )
        if not hasher.verify_password(data.password, settings.app_admin_password):
            logger.error("Invalid password", username=data.username)
            raise AuthError(
                "Invalid password.",
                context={"username": data.username, "reason": "password_mismatch"},
            )
        logger.info("User logged in successfully", username=data.username)
        return True
