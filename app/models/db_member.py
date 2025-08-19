"""Model Untuk Member / Concumer API / Otomax dan lain lain."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.properties import MappedColumn

from app.models import Base
from app.models.audit_mixin import AuditMixin


class Member(Base, AuditMixin):
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

    # Audit fields & methods inherited from AuditMixin

    def __repr__(self) -> str:
        return f"<Member memberid={self.memberid} name={self.name}>"

    def __str__(self) -> str:
        return f"Member {self.name} (ID: {self.memberid})"
