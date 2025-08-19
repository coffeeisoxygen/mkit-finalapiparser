"""Test AuthService: login & get_user_from_token.

Arrange: setup session, repo, credential, token, auth service.
Act: call login, decode token, get user from token.
Assert: check token, user info, error handling.
"""

# ruff: noqa
# pyright: reportArgumentType = false
import pytest
from app.custom.exceptions.cst_exceptions import (
    AuthError,
    UserNotFoundError,
    UserPasswordError,
)
from app.database.repositories.repo_user import SQLiteUserRepository
from app.service.auth.auth_service import AuthService
from app.service.auth.credential_service import CredentialService
from app.service.auth.token_service import TokenService


@pytest.mark.asyncio
async def test_authservice_login_and_get_user(monkeypatch):
    # Arrange
    class DummySession:
        pass

    class DummyRepo:
        async def get_by_username(self, username):
            if username == "admin":
                return type(
                    "User",
                    (),
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "full_name": "Admin User",
                        "is_superuser": True,
                        "is_active": True,
                        "hashed_password": "hashedpass",
                    },
                )()
            return None

    class DummyHasher:
        def verify_value(self, plain, hashed):
            return plain == "password" and hashed == "hashedpass"

    # Patch repo in CredentialService
    monkeypatch.setattr(
        SQLiteUserRepository, "__init__", lambda self, session, autocommit=True: None
    )
    monkeypatch.setattr(
        SQLiteUserRepository, "get_by_username", DummyRepo().get_by_username
    )
    session = DummySession()
    cred = CredentialService(session, hasher=DummyHasher())
    token = TokenService("secret", "HS256", 10)
    auth = AuthService(cred, token)

    # Act
    jwt_token = await auth.login("admin", "password")
    user = auth.get_user_from_token(jwt_token)

    # Assert
    assert isinstance(jwt_token, str)
    assert user.username == "admin"
    assert user.is_superuser is True
    assert user.is_active is True
    assert user.email == "admin@example.com"
    assert user.full_name == "Admin User"
    # New: assert user.id exists and token payload contains id
    decoded = token.decode_token(jwt_token)
    assert "id" in decoded
    assert decoded["id"] == user.id
    assert decoded["username"] == user.username


@pytest.mark.asyncio
async def test_authservice_login_invalid_user(monkeypatch):
    class DummySession:
        pass

    class DummyRepo:
        async def get_by_username(self, username):
            return None

    class DummyHasher:
        def verify_value(self, plain, hashed):
            return True

    monkeypatch.setattr(
        SQLiteUserRepository, "__init__", lambda self, session, autocommit=True: None
    )
    monkeypatch.setattr(
        SQLiteUserRepository, "get_by_username", DummyRepo().get_by_username
    )
    session = DummySession()
    cred = CredentialService(session, hasher=DummyHasher())
    token = TokenService("secret", "HS256", 10)
    auth = AuthService(cred, token)
    with pytest.raises(UserNotFoundError):
        await auth.login("notfound", "password")


@pytest.mark.asyncio
async def test_authservice_login_invalid_password(monkeypatch):
    class DummySession:
        pass

    class DummyRepo:
        async def get_by_username(self, username):
            return type(
                "User",
                (),
                {
                    "id": 1,  # tambahkan id
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "Admin User",
                    "is_superuser": True,
                    "is_active": True,
                    "hashed_password": "hashedpass",
                },
            )()

    class DummyHasher:
        def verify_value(self, plain, hashed):
            return False

    monkeypatch.setattr(
        SQLiteUserRepository, "__init__", lambda self, session, autocommit=True: None
    )
    monkeypatch.setattr(
        SQLiteUserRepository, "get_by_username", DummyRepo().get_by_username
    )
    session = DummySession()
    cred = CredentialService(session, hasher=DummyHasher())
    token = TokenService("secret", "HS256", 10)
    auth = AuthService(cred, token)
    with pytest.raises(UserPasswordError):
        await auth.login("admin", "wrongpass")


@pytest.mark.asyncio
async def test_authservice_get_user_from_token_invalid(monkeypatch):
    cred = CredentialService(None, hasher=None)
    token = TokenService("secret", "HS256", 10)
    auth = AuthService(cred, token)
    # Token with missing fields
    import jwt

    bad_token = jwt.encode({"exp": 123}, "secret", algorithm="HS256")
    with pytest.raises(AuthError):
        auth.get_user_from_token(bad_token)
