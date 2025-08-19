"""Model Untuk Member / Concumer API / Otomax dan lain lain."""

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.properties import MappedColumn

from app.models import Base


class Member(Base):
    """schema untuk member/ reseller yang akan menggunakan API melalu Sistem Lain."""

    __tablename__ = "members"

    memberid: MappedColumn[str] = mapped_column(
        String(32), index=True, nullable=False, unique=True, primary_key=True
    )
    name: MappedColumn[str] = mapped_column(String(100), nullable=False)
    ipaddress: MappedColumn[str] = mapped_column(
        String(45), nullable=False
    )  # cukup utk IPv4/IPv6 teks
    report_url: MappedColumn[str] = mapped_column(
        String(2048), nullable=False
    )  # URL panjang
    pin: MappedColumn[str] = mapped_column(String(255), nullable=False)
    password: MappedColumn[str] = mapped_column(String(255), nullable=False)
    allow_nosign: MappedColumn[bool] = mapped_column(
        Boolean(), default=False, nullable=False
    )
    is_active: MappedColumn[bool] = mapped_column(
        Boolean(), default=True, nullable=False
    )
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
        return f"<Member memberid={self.memberid} name={self.name}>"

    def __str__(self) -> str:
        return f"Member {self.name} (ID: {self.memberid})"
