import uuid


def to_uuid(value: str | uuid.UUID) -> uuid.UUID:
    """Always return UUID object."""
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


def to_uuid_str(value: str | uuid.UUID) -> str:
    """Always return canonical string UUID."""
    return str(to_uuid(value))
