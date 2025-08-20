"""schemas user login / crud."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.ulid import ULID

from app.schemas.cmn_validator import (
    AlphanumericUnderscoreStr,
    AlphanumericWithSpaceStr,
    PasswordStrongStr,
)

# TODO : Implementasi dan rapihakn model , dsini nati harus ada validasi dan json_schema


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
    # NOTE: plain password, nanti di-hash di service


class AdminSeeder(
    UserBase,
):
    """Schema untuk seeding admin user."""

    password: str = Field(
        ..., min_length=6
    )  # NOTE: plain password, nanti di-hash di service
    is_superuser: bool = True
    is_active: bool = True
    is_deleted: bool = False


class UserUpdate(BaseModel):
    """Schema untuk update user (input partial)."""

    username: AlphanumericUnderscoreStr | None = None
    email: EmailStr | None = None
    full_name: AlphanumericWithSpaceStr | None = None
    password: PasswordStrongStr | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


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

    id: ULID  # ULID type for database id
    username: str
    email: str
    full_name: str
    hashed_password: str
    is_superuser: bool
    is_active: bool
    is_deleted: bool
    created_at: datetime | None
    updated_at: datetime | None
    created_by: ULID | None
    updated_by: ULID | None
    deleted_at: datetime | None
    deleted_by: ULID | None

    model_config = {"from_attributes": True, "populate_by_name": True}
