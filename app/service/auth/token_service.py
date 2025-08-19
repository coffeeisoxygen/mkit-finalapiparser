from datetime import UTC, datetime, timedelta

import jwt
from app.custom.exceptions.cst_exceptions import (
    AuthError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.mlogg import logger
from app.schemas.sch_token import UserToken


class TokenService:
    """Create & validate JWT."""

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes
        logger.bind(service="TokenService").debug("TokenService initialized")

    def create_token(self, user: UserToken) -> str:
        """Create JWT token with full user info in payload.

        Args:
            user (UserToken): UserToken schema with user info.

        Returns:
            str: JWT token string.
        """
        expire = datetime.now(UTC) + timedelta(minutes=self.expire_minutes)
        payload = {
            "sub": user.username,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "email": user.email,
            "full_name": user.full_name,
            "exp": expire,
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.bind(service="TokenService").debug(
            "Token created", username=user.username
        )
        return token

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as e:
            logger.bind(service="TokenService").warning("Token expired", token=token)
            raise TokenExpiredError(cause=e) from e
        except jwt.InvalidTokenError as e:
            logger.bind(service="TokenService").warning("Invalid token", token=token)
            raise TokenInvalidError(cause=e) from e
        except Exception as e:
            logger.bind(service="TokenService").error(
                "Authentication error occurred", token=token
            )
            raise AuthError("Authentication error occurred.", cause=e) from e
