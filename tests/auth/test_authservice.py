from datetime import UTC, datetime, timedelta

import jwt
import pytest
from app.custom.exceptions.cst_exceptions import (
    AuthError,
    TokenInvalidError,
    UserNotFoundError,
    UserPasswordError,
)
from app.repositories.rep_user import UserRepository
from app.service import HasherService
from app.service.auth.auth_service import AuthService
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService


class DummyHasher(HasherService):
    def verify_password(self, plain, hashed):  # pyright: ignore[reportIncompatibleMethodOverride]
        return plain == hashed


@pytest.fixture
def user_repo():
    # Use the default fake_users_db with 'Admin' user
    return UserRepository()


@pytest.fixture
def token_service():
    return TokenService(secret_key="secret", algorithm="HS256", expire_minutes=1)


@pytest.fixture
def credential_service(user_repo):
    return CredentialService(user_repo, DummyHasher())


@pytest.fixture
def auth_service(credential_service, token_service, user_repo):
    return AuthService(credential_service, token_service, user_repo)


def test_login_success(auth_service):
    token = auth_service.login(
        "Admin",
        "$argon2id$v=19$m=65536,t=3,p=4$QVjSDjye4dKUnq1sWc4I5A$k477GJHmB0eoQzo5bo+6m8kHzDwfQZfH2zUiYJZt75w",
    )
    assert token is not None


def test_login_wrong_password(auth_service):
    with pytest.raises(UserPasswordError):
        auth_service.login("Admin", "wrongpass")


def test_login_user_not_found(auth_service):
    with pytest.raises(UserNotFoundError):
        auth_service.login("nouser", "password123")


def test_get_user_from_token(auth_service):
    token = auth_service.login(
        "Admin",
        "$argon2id$v=19$m=65536,t=3,p=4$QVjSDjye4dKUnq1sWc4I5A$k477GJHmB0eoQzo5bo+6m8kHzDwfQZfH2zUiYJZt75w",
    )
    user = auth_service.get_user_from_token(token)
    assert user.username == "Admin"


def test_get_user_from_token_invalid(auth_service):
    with pytest.raises(TokenInvalidError):
        auth_service.get_user_from_token("invalidtoken")


def test_get_user_from_token_missing_sub(auth_service, token_service):
    # Create a token with no 'sub' field

    payload = {"exp": token_service.expire_minutes}
    token = jwt.encode(
        payload, token_service.secret_key, algorithm=token_service.algorithm
    )
    with pytest.raises(AuthError):
        auth_service.get_user_from_token(token)


def test_get_user_from_token_user_not_found(auth_service, token_service):
    # Create a token for a user that does not exist

    expire = datetime.now(UTC) + timedelta(minutes=token_service.expire_minutes)
    payload = {"sub": "nouser", "exp": expire}
    token = jwt.encode(
        payload, token_service.secret_key, algorithm=token_service.algorithm
    )
    with pytest.raises(AuthError):
        auth_service.get_user_from_token(token)
