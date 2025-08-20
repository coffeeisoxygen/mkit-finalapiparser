"""ULIDType custom SQLAlchemy type for ULID support.

This module provides a SQLAlchemy TypeDecorator for storing ULID objects
as UUID in the database, and converting them back to ULID on retrieval.
"""

from sqlalchemy.types import CHAR, TypeDecorator
from ulid import ULID


class ULIDType(TypeDecorator):
    """Platform-independent ULID type.

    Uses CHAR(26) for storage, storing ULIDs as their string representation.
    """

    impl = CHAR(26)  # ULIDs are 26 characters long in string form
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, ULID):
            return str(value)
        if isinstance(value, str):
            return value
        raise TypeError(f"Expected ULID object or str, got {type(value)}")

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return ULID.from_str(value)

    def process_literal_param(self, value, dialect):
        if value is None:
            return "NULL"
        return f"'{value!s}'"

    def coerce_compared_value(self, op, value):
        if isinstance(value, str):
            return self.impl
        return self

    @property
    def python_type(self):
        return ULID
