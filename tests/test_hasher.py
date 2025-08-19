"""Unit tests for HasherService (argon2 password hashing)."""

import pytest
from app.service.security.srv_hasher import HasherService


@pytest.mark.parametrize("password", ["password123", "admin", "s3cr3t!"])
def test_hash_and_verify_success(password):
    hasher = HasherService()
    hashed = hasher.hash_value(password)
    assert isinstance(hashed, str)
    assert hasher.verify_value(password, hashed) is True


@pytest.mark.parametrize(
    "password,wrong_password",
    [
        ("password123", "wrongpass"),
        ("admin", "ADMIN"),
        ("s3cr3t!", "s3cr3t!!"),
    ],
)
def test_verify_fail(password, wrong_password):
    hasher = HasherService()
    hashed = hasher.hash_value(password)
    assert hasher.verify_value(wrong_password, hashed) is False
