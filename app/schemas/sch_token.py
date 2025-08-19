# Token Service Goes Here


from pydantic import BaseModel

from app.schemas.sch_user import EmailStr


class UserToken(BaseModel):
    """Schema untuk user token."""

    id: int
    username: str
    email: EmailStr
    full_name: str
    is_superuser: bool
    is_active: bool


class UserPasswordToken(UserToken):
    """Schema untuk user password.

    mengambil password user untuk token
    """

    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    username: str | None = None
    is_superuser: bool = False
