"""ULIDType custom SQLAlchemy type for ULID support.

This module provides a SQLAlchemy TypeDecorator for storing ULID objects
as UUID in the database, and converting them back to ULID on retrieval.
"""

from typing import Any

from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import UUID, TypeDecorator
from ulid import ULID


class ULIDType(TypeDecorator):
    """Custom SQLAlchemy TypeDecorator for ULID.

    Stores ULID as UUID in the database, and converts back to ULID on retrieval.
    """

    impl = UUID  # SQLAlchemy Underlying UUID

    def process_bind_param(self, value: Any | None, dialect: Dialect) -> Any:
        # dialect is required by SQLAlchemy, but not used
        if value is None:
            return value
        if isinstance(value, ULID):
            return value.to_uuid()  # Convert ULID object to uuid.UUID
        if isinstance(value, str):
            return ULID.from_str(value).to_uuid()
        return value

    def process_result_value(self, value: Any | None, dialect: Dialect) -> Any:
        if value is None:
            return value
        return ULID.from_uuid(value)

    cache_ok = True
