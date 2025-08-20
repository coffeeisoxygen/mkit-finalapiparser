import uuid
from typing import Any


# ------------------------
# Record validation
# ------------------------
def valid_record_filter(model: Any) -> Any:
    """Return a SQLAlchemy filter condition for valid (active, not deleted) records."""
    return (
        (model.is_active.is_(True))
        & (model.is_deleted_flag.is_(False))
        & (model.deleted_at.is_(None))
    )


def is_valid_record(model: Any) -> bool:
    """Check if a model instance is valid (active, not deleted)."""
    return bool(model.is_active and not model.is_deleted_flag and not model.deleted_at)


# ------------------------
# UUID helpers (SQLite friendly)
# ------------------------
def to_uuid(value: str | uuid.UUID) -> uuid.UUID:
    """Convert a string or UUID to UUID object."""
    if isinstance(value, uuid.UUID):
        return value
    if isinstance(value, str):
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise ValueError(f"Invalid UUID string: {value}") from e


def to_uuid_str(value: str | uuid.UUID) -> str:
    """Convert a UUID or str to a canonical string UUID."""
    return str(to_uuid(value))


def pk_for_query(value: str | uuid.UUID) -> str:
    """Return a string UUID for primary key queries (SQLite compatible)."""
    return to_uuid_str(value)
