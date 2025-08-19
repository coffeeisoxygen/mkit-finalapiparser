"""Your Enhanced Decorator - Production Ready Version.

dengan additional improvements untuk robustness
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, mapped_column
from sqlalchemy.sql import Select

if TYPE_CHECKING:
    pass


def _add_audit_fields(cls):
    """Assign audit columns to the model class."""
    cls.created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created",
        index=True,
    )
    cls.updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated",
        index=True,
    )
    cls.deleted_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when record was soft deleted (NULL = active)",
        index=True,
    )
    cls.created_by = mapped_column(
        Integer,
        nullable=True,
        comment="ID of user who created this record",
        index=True,
    )
    cls.updated_by = mapped_column(
        Integer, nullable=True, comment="ID of user who last updated this record"
    )
    cls.deleted_by = mapped_column(
        Integer, nullable=True, comment="ID of user who soft deleted this record"
    )
    return cls


def _add_audit_instance_methods(cls):
    """Assign audit instance methods to the model class."""

    def soft_delete(self, user_id: int | None = None) -> bool:
        try:
            self.deleted_at = datetime.now()
            if hasattr(self, "deleted_by"):
                self.deleted_by = user_id
            if hasattr(self, "on_soft_delete"):
                result = self.on_soft_delete(user_id)
                return result is not False
            else:
                return True
        except Exception as e:
            if hasattr(self, "_audit_logger"):
                self._audit_logger.error(f"Soft delete failed: {e}")
            return False

    def restore(self) -> bool:
        try:
            if not self.is_deleted:
                return False
            self.deleted_at = None
            if hasattr(self, "deleted_by"):
                self.deleted_by = None
            if hasattr(self, "on_restore"):
                result = self.on_restore()
                return result is not False
            else:
                return True
        except Exception as e:
            if hasattr(self, "_audit_logger"):
                self._audit_logger.error(f"Restore failed: {e}")
            return False

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

    def audit_info(self) -> dict:
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
            "created_by": getattr(self, "created_by", None),
            "updated_by": getattr(self, "updated_by", None),
            "deleted_by": getattr(self, "deleted_by", None),
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
        }

    cls.soft_delete = soft_delete
    cls.restore = restore
    cls.is_deleted = is_deleted
    cls.is_active = is_active
    cls.audit_info = audit_info
    return cls


def _add_audit_class_methods(cls):
    """Assign audit class methods to the model class."""

    @classmethod
    def query_active(cls):
        return select(cls).where(cls.deleted_at.is_(None))

    @classmethod
    def query_deleted(cls):
        return select(cls).where(cls.deleted_at.isnot(None))

    @classmethod
    def query_by_user(cls, user_id: int, include_deleted: bool = False):
        base_query = select(cls).where(cls.created_by == user_id)
        if not include_deleted:
            return base_query.where(cls.deleted_at.is_(None))
        return base_query

    @classmethod
    def bulk_soft_delete(
        cls, session: Session, ids: list[int], user_id: int | None = None
    ):
        try:
            if not ids:
                return 0
            update_data = {
                cls.deleted_at: datetime.now(),
                cls.deleted_by: user_id,
            }
            result = (
                session.query(cls)
                .filter(
                    cls.id.in_(ids),
                    cls.deleted_at.is_(None),
                )
                .update(
                    update_data,
                    synchronize_session="fetch",
                )
            )
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    @classmethod
    def bulk_restore(cls, session: Session, ids: list[int]):
        try:
            if not ids:
                return 0
            result = (
                session.query(cls)
                .filter(
                    cls.id.in_(ids),
                    cls.deleted_at.isnot(None),
                )
                .update(
                    {"deleted_at": None, "deleted_by": None},
                    synchronize_session="fetch",
                )
            )
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    @classmethod
    def count_active(cls, session: Session):
        return session.query(cls).filter(cls.deleted_at.is_(None)).count()

    @classmethod
    def count_deleted(cls, session: Session):
        return session.query(cls).filter(cls.deleted_at.isnot(None)).count()

    cls.query_active = query_active
    cls.query_deleted = query_deleted
    cls.query_by_user = query_by_user
    cls.bulk_soft_delete = bulk_soft_delete
    cls.bulk_restore = bulk_restore
    cls.count_active = count_active
    cls.count_deleted = count_deleted
    return cls


def auditable(cls: type) -> type:
    """Decorator untuk menambahkan audit fields dan methods ke SQLAlchemy model."""
    _add_audit_fields(cls)
    _add_audit_instance_methods(cls)
    _add_audit_class_methods(cls)
    return cls


# ============================================================================
# ENHANCED MINIMAL DECORATORS
# ============================================================================


def timestamps_only(cls: type) -> type:
    """Minimal decorator - hanya timestamps dengan performance optimizations."""
    cls.created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,  # Performance enhancement
    )
    cls.updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )

    # Utility method
    def age_in_days(self) -> int:
        """Calculate age of record in days."""
        if self.created_at:
            return (datetime.now() - self.created_at.replace(tzinfo=None)).days
        return 0

    cls.age_in_days = age_in_days

    return cls


def soft_deletable(cls: type) -> type:
    """Enhanced soft delete decorator dengan better query support."""
    cls.deleted_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,  # Critical untuk performance
    )

    def soft_delete(self):
        self.deleted_at = datetime.now()
        if hasattr(self, "on_soft_delete"):
            self.on_soft_delete()

    def restore(self):
        self.deleted_at = None
        if hasattr(self, "on_restore"):
            self.on_restore()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    # Enhanced query methods
    @classmethod
    def query_active(cls) -> Select:
        """Return SQLAlchemy Select for active records only."""
        return select(cls).where(cls.deleted_at.is_(None))

    @classmethod
    def query_deleted(cls) -> Select:
        """Return SQLAlchemy Select for soft deleted records only."""
        return select(cls).where(cls.deleted_at.isnot(None))

    cls.soft_delete = soft_delete
    cls.restore = restore
    cls.is_deleted = is_deleted
    cls.query_active = query_active
    cls.query_deleted = query_deleted

    return cls


# # ============================================================================
# # USAGE EXAMPLES WITH YOUR ENHANCEMENTS
# # ============================================================================


# # Your enhanced decorator in action:
# @auditable
# class User(Base):
#     __tablename__ = "users"

#     id = mapped_column(Integer, primary_key=True)
#     username = mapped_column(String, unique=True, nullable=False)
#     email = mapped_column(String, unique=True, nullable=False)

#     # Optional: Custom event hooks
#     def on_soft_delete(self, user_id: int | None = None) -> bool:
#         """Custom logic saat user di-soft delete."""
#         # Log activity, send notification, etc.
#         print(f"User {self.username} soft deleted by user {user_id}")
#         return True  # Allow deletion

#     def on_restore(self) -> bool:
#         """Custom logic saat user di-restore."""
#         print(f"User {self.username} restored")
#         return True  # Allow restore


# # Usage examples:
# def example_usage():
#     """Examples of using your enhanced decorator."""

#     # Basic operations
#     user = User(username="john", email="john@example.com")
#     session.add(user)
#     session.commit()

#     # Soft delete dengan user tracking
#     user.soft_delete(user_id=123)

#     # Query operations
#     active_users = User.query_active().all()
#     deleted_users = User.query_deleted().all()
#     user_records = User.query_by_user(user_id=123).all()

#     # Bulk operations
#     User.bulk_soft_delete(session, [1, 2, 3], user_id=456)
#     User.bulk_restore(session, [1, 2])

#     # Audit info
#     audit_data = user.audit_info()

#     # Statistics
#     active_count = User.count_active(session)
#     deleted_count = User.count_deleted(session)
#     session.commit()

#     # Soft delete dengan user tracking
#     user.soft_delete(user_id=123)

#     # Query operations
#     active_users = User.query_active().all()
#     deleted_users = User.query_deleted().all()
#     user_records = User.query_by_user(user_id=123).all()

#     # Bulk operations
#     User.bulk_soft_delete(session, [1, 2, 3], user_id=456)
#     User.bulk_restore(session, [1, 2])

#     # Audit info
#     audit_data = user.audit_info()

#     # Statistics
#     active_count = User.count_active(session)
#     deleted_count = User.count_deleted(session)
