"""Model Untuk Member / Concumer API / Otomax dan lain lain."""

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import mapped_column

from app.models import Base


class Member(Base):
    __tablename__ = "members"

    id = mapped_column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    memberid = mapped_column(String(32), index=True, nullable=False, unique=True)
    name = mapped_column(String(100), nullable=False)
    ipaddress = mapped_column(String(45), nullable=False)  # cukup utk IPv4/IPv6 teks
    report_url = mapped_column(String(2048), nullable=False)  # URL panjang
    hash_pin = mapped_column(String(255), nullable=False)
    hash_password = mapped_column(String(255), nullable=False)
    is_active = mapped_column(Boolean(), default=True, nullable=False)
    allow_nosign = mapped_column(Boolean(), default=False, nullable=False)
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
        return f"<Member id={self.id} memberid={self.memberid} name={self.name}>"

    def __str__(self) -> str:
        return f"Member {self.name} (ID: {self.id})"
