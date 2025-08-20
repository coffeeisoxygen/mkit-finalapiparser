from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.db_mixin import TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Audit log generic & reusable."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    description: Mapped[dict | str] = mapped_column(JSON, nullable=False)
    detail: Mapped[JSON | None] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"<AuditLog id={self.id} timestamp={self.timestamp}>"
