"""Schema for audit fields (actor/audit trail).

This schema is used for representing audit fields in API responses or internal usage.
"""

from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_extra_types.ulid import ULID as ULID_SCHEMA
from ulid import ULID as ULID_DB


class ActorAuditFields(BaseModel):
    """Schema for audit and soft delete fields.

    Attributes:
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
        deleted_at: Timestamp when the record was soft deleted.
        deleted_by: ULID of the user who deleted the record.
        created_by: ULID of the user who created the record.
        updated_by: ULID of the user who last updated the record.
    """

    created_at: datetime | None = Field(
        default=None, description="Timestamp saat record dibuat"
    )
    updated_at: datetime | None = Field(
        default=None, description="Timestamp saat record diupdate"
    )
    deleted_at: datetime | None = Field(
        default=None, description="Timestamp saat record dihapus (soft delete)"
    )
    deleted_by: ULID_SCHEMA | None = Field(
        default=None, description="User ID yang menghapus record"
    )
    created_by: ULID_SCHEMA | None = Field(
        default=None, description="User ID yang membuat record"
    )
    updated_by: ULID_SCHEMA | None = Field(
        default=None, description="User ID yang mengupdate record"
    )

    @field_validator("deleted_by", "created_by", "updated_by", mode="before")
    @classmethod
    def ulid_from_any(cls, v: str | ULID_SCHEMA | ULID_DB | None) -> ULID_SCHEMA | None:
        """Convert various types to ULID_SCHEMA."""
        if v is None or isinstance(v, ULID_SCHEMA):
            return v
        if isinstance(v, ULID_DB):
            return ULID_SCHEMA.from_str(str(v))
        if isinstance(v, str):
            return ULID_SCHEMA.from_str(v)
        raise ValidationError(f"Invalid ULID type: {type(v)}")

    @staticmethod
    def str_to_ulid(value: str | None) -> ULID_SCHEMA | None:
        """Helper to convert str to ULID or None.

        Args:
            value: ULID string or None.

        Returns:
            ULID instance or None.
        """
        if value is None:
            return None
        return ULID_SCHEMA.from_str(str(value))

    model_config = {"from_attributes": True, "populate_by_name": True}
