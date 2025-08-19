"""schemas user login / crud."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema untuk membuat user (input)."""

    password: str  # NOTE: plain password, nanti di-hash di service


class UserUpdate(BaseModel):
    """Schema untuk update user (partial)."""

    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserPublic(UserBase):
    """Schema untuk response ke client (tanpa password)."""

    id: int
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserInDB(BaseModel):
    """Schema representasi user di database.

    internal Use ya.
    """

    id: int
    username: str
    email: str | None
    full_name: str | None
    hashed_password: str
    is_superuser: bool
    created_at: datetime | None
    updated_at: datetime | None
    created_by: int | None
    updated_by: int | None
    deleted_at: datetime | None
    deleted_by: int | None

    model_config = {"from_attributes": True, "populate_by_name": True}


class AdminSeeder(UserBase):
    """Schema untuk seeding admin user."""

    password: str
    is_superuser: bool = True
    is_active: bool = True
    is_deleted: bool = False


# Token Service Goes Here
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserLogin(BaseModel):
    """Schema untuk user login request."""

    username: str
    hashed_password: str

    model_config = {"from_attributes": True, "populate_by_name": True}
