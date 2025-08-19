from app.schemas.sch_user import UserInDBD

fake_users_db = {
    "Admin": {
        "username": "Admin",
        "full_name": "Admin Ganteng",
        "email": "admin@ganteng.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$QVjSDjye4dKUnq1sWc4I5A$k477GJHmB0eoQzo5bo+6m8kHzDwfQZfH2zUiYJZt75w",
        "disabled": False,
    }
}


class UserRepository:
    """Simple user repository using dict backend."""

    def __init__(self, db=None):  # noqa: ANN001
        self._db = db or fake_users_db

    def get(self, username: str):
        user_dict = self._db.get(username)
        return UserInDBD(**user_dict) if user_dict else None

    def all(self):
        return [UserInDBD(**user) for user in self._db.values()]
