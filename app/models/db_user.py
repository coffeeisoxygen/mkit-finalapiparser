from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import mapped_column

from app.models import Base


class User(Base):
    """schema untuk user / admin atau pengelola API."""

    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, unique=True, nullable=False)
    email = mapped_column(String, unique=True, nullable=False)
    full_name = mapped_column(String, nullable=False)
    hashed_password = mapped_column(String, nullable=False)
    is_active = mapped_column(Boolean, default=True)
    is_superuser = mapped_column(Boolean, default=False)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} full_name={self.full_name}>"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, full_name={self.full_name})"
