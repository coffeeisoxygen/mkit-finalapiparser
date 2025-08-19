from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.audit_mixin import AuditMixin
from app.models.ulid_type import ULID, ULIDType


class User(Base, AuditMixin):
    """schema untuk user / admin atau pengelola API."""

    __tablename__ = "users"

    id: Mapped[ULID] = mapped_column(
        ULIDType(), primary_key=True, default=lambda: ULID()
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_deleted_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Audit fields & methods inherited from AuditMixin

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} full_name={self.full_name}>"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, full_name={self.full_name})"
