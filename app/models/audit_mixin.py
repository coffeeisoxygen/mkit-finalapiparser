"""AuditMixin: Base class for audit and soft delete fields/methods.

Can be inherited by any SQLAlchemy model for standardized audit trail.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    """Audit and soft delete functionality for SQLAlchemy models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    deleted_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    """Audit and soft delete functionality for SQLAlchemy models.

    Fields:
        created_at: Timestamp saat record dibuat
        updated_at: Timestamp saat record diupdate
        created_by: User ID yang membuat record
        updated_by: User ID yang mengupdate record
        deleted_at: Timestamp saat record dihapus (soft delete)
        deleted_by: User ID yang menghapus record
    """

    def soft_delete(self, user_id=None):  # noqa: ANN001
        """Mark record as soft deleted."""
        self.deleted_at = datetime.now(UTC)
        self.deleted_by = user_id

    def restore(self):
        """Restore soft deleted record."""
        self.deleted_at = None
        self.deleted_by = None

    @property
    def is_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None

    @property
    def is_active(self):
        """Check if record is active (not deleted)."""
        return self.deleted_at is None
