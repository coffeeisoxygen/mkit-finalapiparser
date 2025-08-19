from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.properties import MappedColumn

from app.models import Base


class User(Base):
    """schema untuk user / admin atau pengelola API."""

    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    username: MappedColumn[str] = mapped_column(String, unique=True, nullable=False)
    email: MappedColumn[str] = mapped_column(String, unique=True, nullable=False)
    full_name: MappedColumn[str] = mapped_column(String, nullable=False)
    hashed_password: MappedColumn[str] = mapped_column(String, nullable=False)
    is_active: MappedColumn[bool] = mapped_column(Boolean, default=True)
    is_superuser: MappedColumn[bool] = mapped_column(Boolean, default=False)

    created_at: MappedColumn[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    updated_at: MappedColumn[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    is_deleted: MappedColumn[bool] = mapped_column(
        Boolean(), default=False, nullable=False
    )
    deleted_at: MappedColumn[DateTime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} full_name={self.full_name}>"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, full_name={self.full_name})"
