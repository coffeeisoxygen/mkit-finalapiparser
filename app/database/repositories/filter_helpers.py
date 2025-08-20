"""Standardized filter and status helpers for AuditMixin models.

These helpers provide SQLAlchemy filter conditions and instance status checks for models
implementing audit/soft delete logic (is_active, is_deleted_flag, deleted_at).

All helpers are generic and can be used for any model with AuditMixin fields.
"""

from typing import Any


# ------------------------
# SQLAlchemy filter helpers
# ------------------------
def valid_record_filter(model: Any) -> Any:
    """Filter for valid (active, not deleted) records.

    Args:
        model: ORM model class.

    Returns:
        SQLAlchemy filter condition.
    """
    return (model.is_active.is_(True)) & (model.is_deleted_flag.is_(False))


def soft_deleted_filter(model: Any) -> Any:
    """Filter for soft-deleted records.

    Args:
        model: ORM model class.

    Returns:
        SQLAlchemy filter condition.
    """
    return model.is_deleted_flag.is_(True)


def inactive_filter(model: Any) -> Any:
    """Filter for inactive (not deleted) records.

    Args:
        model: ORM model class.

    Returns:
        SQLAlchemy filter condition.
    """
    return (model.is_active.is_(False)) & (model.is_deleted_flag.is_(False))


def all_records_filter(model: Any) -> Any:
    """No filter: returns all records (for admin/audit queries).

    Args:
        model: ORM model class.

    Returns:
        SQLAlchemy filter condition (always True).
    """
    return True


# ------------------------
# Instance status helpers
# ------------------------
def is_valid_record(instance: Any) -> bool:
    """Check if instance is valid (active, not deleted).

    Args:
        instance: ORM model instance.

    Returns:
        bool: True if valid.
    """
    return bool(
        getattr(instance, "is_active", False)
        and not getattr(instance, "is_deleted_flag", False)
    )


def is_soft_deleted(instance: Any) -> bool:
    """Check if instance is soft deleted.

    Args:
        instance: ORM model instance.

    Returns:
        bool: True if soft deleted.
    """
    return bool(getattr(instance, "is_deleted_flag", False))


def is_inactive(instance: Any) -> bool:
    """Check if instance is inactive (not deleted).

    Args:
        instance: ORM model instance.

    Returns:
        bool: True if inactive.
    """
    return bool(
        not getattr(instance, "is_active", True)
        and not getattr(instance, "is_deleted_flag", False)
    )
