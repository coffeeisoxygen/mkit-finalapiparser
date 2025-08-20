"""schemas user login / crud."""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.cmn_validator import (
    AlphanumericUnderscoreStr,
    AlphanumericWithSpaceStr,
    PasswordStrongStr,
)


class UserFilterType(StrEnum):
    VALID = "valid"
    INACTIVE = "inactive"
    SOFT_DELETED = "soft_deleted"
    ALL = "all"


class UserBase(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    username: AlphanumericUnderscoreStr = Field(
        description="username untuk login , hanya alphanumeric dan underscore"
    )
    email: EmailStr
    full_name: AlphanumericWithSpaceStr = Field(
        description="full name untuk login , hanya alphanumeric dan spasi"
    )


class UserCreate(UserBase):
    """Schema untuk membuat user (input)."""

    password: PasswordStrongStr = Field(
        description="Password untuk user baru, harus kuat dan tidak boleh mengandung spasi."
    )


class AdminSeeder(
    UserBase,
):
    """Schema untuk seeding admin user."""

    id: uuid.UUID
    password: str = Field(..., min_length=6)
    is_superuser: bool = True
    is_active: bool = True
    is_deleted: bool = False


class UserUpdateProfile(BaseModel):
    """Schema untuk update user (input partial)."""

    username: AlphanumericUnderscoreStr | None = None
    email: EmailStr | None = None
    full_name: AlphanumericWithSpaceStr | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserPasswordChange(BaseModel):
    """Schema untuk mengubah password user."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    password: PasswordStrongStr | None = None
    repeat_password: PasswordStrongStr | None = None
    new_password: PasswordStrongStr | None = None

    @model_validator(mode="after")
    def check_password_not_same(self):
        """Validasi agar password lama dan baru tidak sama, dan repeat password harus sama."""
        if (
            self.password
            and self.repeat_password
            and self.password != self.repeat_password
        ):
            raise ValueError("Password dan repeat password harus sama")
        if self.password and self.new_password and self.password == self.new_password:
            raise ValueError("Password baru tidak boleh sama dengan password lama")
        return self


class UserResponse(BaseModel):
    """Schema untuk response ke client (tanpa password)."""

    username: AlphanumericUnderscoreStr
    email: EmailStr
    full_name: AlphanumericWithSpaceStr
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserInDB(BaseModel):
    """Schema representasi user di database.

    internal Use ya.
    dont gunakan ini untuk user public/ response Keluar
    untuk kebutuhan repository sih ini agar ngga pusing.
    """

    id: uuid.UUID
    username: str
    email: str
    full_name: str
    hashed_password: str
    is_superuser: bool
    is_active: bool
    is_deleted: bool
    created_at: datetime | None
    updated_at: datetime | None
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    deleted_at: datetime | None
    deleted_by: uuid.UUID | None

    model_config = {"from_attributes": True, "populate_by_name": True}
