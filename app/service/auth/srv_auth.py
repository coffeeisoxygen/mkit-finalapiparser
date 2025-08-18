from datetime import UTC, datetime, timedelta

import jwt

from app.custom.exceptions.cst_exceptions import (
    AuthError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.mlogg import logger


class AuthService:
    """Service khusus untuk ngurus JWT (create & verify)."""

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes
        self.log = logger.bind(service="AuthService")

    def create_access_token(self, subject: str) -> str:
        """Bikin JWT token dengan expiry."""
        expire = datetime.now(UTC) + timedelta(minutes=self.expire_minutes)
        payload = {"sub": subject, "exp": expire}
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.log.info("Access token created", subject=subject, exp=str(expire))
        return token

    def decode_token(self, token: str) -> dict:
        """Decode JWT, return payload dict."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as e:
            self.log.error("Token expired", error=str(e))
            raise TokenExpiredError(cause=e) from e
        except jwt.InvalidTokenError as e:
            self.log.error("Invalid token", error=str(e))
            raise TokenInvalidError(cause=e) from e
        except Exception as e:
            self.log.error("Unexpected auth error", error=str(e))
            raise AuthError("Unexpected authentication error", cause=e) from e
