from app.custom.exceptions.cst_exceptions import AuthError
from app.schemas.sch_token import UserToken
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService


class AuthService:
    """Facade: login → token, token → user info (stateless, dari JWT payload)."""

    def __init__(
        self,
        credential_service: CredentialService,
        token_service: TokenService,
    ):
        self.cred = credential_service
        self.token = token_service

    async def login(self, username: str, password: str) -> str:
        """Login user, return JWT token jika sukses.

        Args:
            username (str): Username user.
            password (str): Password plain user.

        Returns:
            str: JWT token string.
        """
        user = await self.cred.authenticate(username, password)
        # user: UserPasswordToken (schema, sudah include info user)
        user_token = UserToken(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        )
        return self.token.create_token(user_token)

    def get_user_from_token(self, token: str) -> UserToken:
        """Ambil info user dari JWT token (tanpa query DB).

        Args:
            token (str): JWT token string.

        Returns:
            UserToken: Info user dari payload JWT.
        """
        payload = self.token.decode_token(token)
        try:
            return UserToken(
                username=payload.get("sub") or "",
                email=payload.get("email") or "",
                full_name=payload.get("full_name") or "",
                is_superuser=payload.get("is_superuser", False),
                is_active=payload.get("is_active", True),
            )
        except Exception as e:
            raise AuthError(f"Invalid token payload: {e}") from e
