from datetime import UTC, datetime, timedelta

import jwt

from app.custom.cst_exceptions import AuthError, TokenExpiredError, TokenInvalidError
from app.schemas.sch_user import UserInDB
from app.service.srv_hasher import HasherService
from mlogg import logger


class AuthService:
    """Service for authentication and JWT token management.
    Handles user authentication, token creation, and token validation.
    """

    def __init__(
        self, secret_key, algorithm, expire_minutes, user_repo, hasher: HasherService
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes
        self.user_repo = user_repo
        self.hasher = hasher
        self.log = logger.bind(service="AuthService")

    def authenticate_user(self, username: str, password: str) -> UserInDB | None:
        """Authenticate user by username and password."""
        log = self.log.bind(operation="authenticate_user", username=username)
        user = self.user_repo.get(username)
        if not user:
            log.warning("User not found.")
            return None
        if not self.hasher.verify_password(password, user.hashed_password):
            log.warning("Password verification failed.")
            return None
        log.info("User authenticated successfully.")
        return user

    def create_access_token(self, username: str) -> str:
        """Create JWT access token for a user."""
        log = self.log.bind(operation="create_access_token", username=username)
        expire = datetime.now(UTC) + timedelta(minutes=self.expire_minutes)
        payload = {"sub": username, "exp": expire}
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        log.info("Access token created.", expire=str(expire))
        return token

    def _decode_token(self, token: str):
        """Decode JWT token and return payload."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as e:
            self.log.error("Token expired.", error=str(e))
            raise TokenExpiredError(cause=e) from e
        except jwt.InvalidTokenError as e:
            self.log.error("Invalid token.", error=str(e))
            raise TokenInvalidError(cause=e) from e
        except Exception as e:
            self.log.error("Authentication error occurred.", error=str(e))
            raise AuthError("Authentication error occurred.", cause=e) from e

    def _get_user_by_username(self, username: str):
        """Retrieve user by username."""
        user = self.user_repo.get(username)
        if not user:
            self.log.error("User not found for token.", username=username)
            raise AuthError("User not found for token.")
        return user

    def get_user_from_token(self, token: str) -> UserInDB | None:
        """Validate JWT token and return associated user."""
        log = self.log.bind(operation="get_user_from_token")
        payload = self._decode_token(token)
        username = payload.get("sub")
        log = log.bind(username=username)
        if not username:
            log.error("Token payload missing 'sub' (username).")
            raise AuthError("Token payload missing 'sub' (username).")
        user = self._get_user_by_username(username)
        log.info("User retrieved from token.")
        return user
