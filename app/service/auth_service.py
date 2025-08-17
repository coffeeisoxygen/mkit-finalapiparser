from app.config import Settings
from app.custom.cst_exceptions import AuthError
from app.schemas.sch_user import UserLogin
from app.service.srv_hasher import HasherService
from mlogg import logger


class AuthService:
    def __init__(self, settings: Settings, hasher: HasherService):
        self.settings = settings
        self.hasher = hasher

    def login(self, data: UserLogin) -> bool:
        log = logger.bind(username=data.username, operation="login")
        if data.username != self.settings.app_admin_username:
            log.error("Invalid username")
            raise AuthError(
                "Invalid username.",
                context={"username": data.username, "reason": "username_mismatch"},
            )

        if not self.hasher.verify_password(
            data.password, self.settings.app_admin_password
        ):
            log.error("Invalid password")
            raise AuthError(
                "Invalid password.",
                context={"username": data.username, "reason": "password_mismatch"},
            )

        log.info("User logged in successfully")
        return True
