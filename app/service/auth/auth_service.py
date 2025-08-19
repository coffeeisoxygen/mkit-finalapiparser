# app/service/auth/auth_service.py
from app.custom.exceptions.cst_exceptions import AuthError
from app.repositories.memory.rep_user import UserRepository
from app.schemas.sch_user import UserInDBD
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService


class AuthService:
    """Facade: login → token, token → user."""

    def __init__(
        self,
        credential_service: CredentialService,
        token_service: TokenService,
        user_repo: UserRepository,
    ):
        self.cred = credential_service
        self.token = token_service
        self.user_repo = user_repo

    # ---- login flow ----
    def login(self, username: str, password: str) -> str | None:
        user = self.cred.authenticate(username, password)
        if not user:
            return None
        return self.token.create_token(user.username)

    # ---- token → user ----
    def get_user_from_token(self, token: str) -> UserInDBD:
        payload = self.token.decode_token(token)
        username = payload.get("sub")
        if not username:
            raise AuthError("Token payload missing 'sub' (username).")
        user = self.user_repo.get(username)
        if not user:
            raise AuthError("User not found for token.")
        return user
