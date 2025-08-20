import uuid


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
