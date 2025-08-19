"""schemas user login."""

from datetime import datetime

from pydantic import BaseModel

# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class TokenData(BaseModel):
#     username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDBD(User):
#     hashed_password: str


class UserInDB(BaseModel):
    """one on One With Database Model in Database."""

    model_config = {"from_attributes": True, "populate_by_name": True}
    id: int | None
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
