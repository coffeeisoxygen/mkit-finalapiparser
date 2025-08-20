"""fungsi fungsi helper generic shared among queries."""

import uuid
from typing import Any


def valid_record_filter(model: Any) -> Any:
    """Validates the record query for the given model.

    This function constructs a query condition to filter valid records
    based on their active status, deletion status, and deletion timestamp.

    Args:
        model (_type_): model yang akan divalidasi

    Returns:
        _type_: kondisi query untuk validasi record
    """
    return (
        (model.is_active.is_(True))
        & (model.is_deleted_flag.is_(False))
        & (model.deleted_at.is_(None))
    )


def is_valid_record(model: Any) -> bool:
    return model.is_active and not model.is_deleted_flag and not model.deleted_at


def to_uuid_str(value: str | uuid.UUID) -> str:
    """Convert a UUID or str to a string UUID for SQLite queries."""
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, str):
        try:
            return str(uuid.UUID(value))
        except Exception:
            return value
    raise ValueError(
        f"to_uuid_str only accepts str or UUID, got {type(value).__name__}"
    )


def to_uuid(value: str | uuid.UUID) -> uuid.UUID:
    """Convert a str or UUID to UUID object."""
    if isinstance(value, uuid.UUID):
        return value
    if isinstance(value, str):
        return uuid.UUID(value)
    raise ValueError(f"to_uuid only accepts str or UUID, got {type(value).__name__}")
