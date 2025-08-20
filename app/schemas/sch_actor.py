"""Schema for audit fields (actor/audit trail).

This schema is used for representing audit fields in API responses or internal usage.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_extra_types.ulid import ULID as ULID_SCHEMA


class ActorAuditFields(BaseModel):
    """Schema for audit and soft delete fields.

    Attributes:
        created_at: Timestamp saat record dibuat.
        updated_at: Timestamp saat record diupdate.
        deleted_at: Timestamp saat record dihapus (soft delete).
        deleted_by: ULID user yang menghapus record.
        created_by: ULID user yang membuat record.
        updated_by: ULID user yang mengupdate record.
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


class ActorBase(BaseModel):
    """Minimal schema untuk representasi actor/user.

    Attributes:
        id: ULID user.
        username: Nama pengguna.
        full_name: Nama lengkap pengguna.
    """

    id: ULID_SCHEMA
    username: str
    full_name: str


class ActorReference(BaseModel):
    """Schema referensi actor/user untuk audit fields.

    Attributes:
        id: ULID user.
        name: Nama pengguna (opsional).
    """

    id: ULID_SCHEMA
    name: str | None = None


class AuditActionLog(BaseModel):
    """Schema untuk log aktivitas/audit trail.

    Attributes:
        id: ULID log.
        actor_id: ULID actor yang melakukan aksi.
        action: Nama aksi/event.
        target_type: Tipe target (misal: 'user', 'module').
        target_id: ULID target.
        timestamp: Waktu aksi.
        metadata: Info tambahan (opsional).
    """

    id: ULID_SCHEMA
    actor_id: ULID_SCHEMA
    action: str
    target_type: str
    target_id: ULID_SCHEMA | None = None
    timestamp: datetime
    metadata: dict | None = None


class SoftDeleteSchema(BaseModel):
    """Schema untuk response/command soft delete.

    Attributes:
        deleted_by: ULID user yang menghapus.
        deleted_at: Waktu penghapusan.
    """

    deleted_by: ULID_SCHEMA
    deleted_at: datetime
