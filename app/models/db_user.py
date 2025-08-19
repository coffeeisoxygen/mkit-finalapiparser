from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.audit_mixin import AuditMixin


class User(Base, AuditMixin):
    """schema untuk user / admin atau pengelola API."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit fields & methods inherited from AuditMixin

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} full_name={self.full_name}>"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, full_name={self.full_name})"
