"""hasher service using argon."""

from argon2 import PasswordHasher


class HasherService:
    def __init__(self):
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            self._hasher.verify(hashed, password)
        except Exception:
            return False
        else:
            return True
