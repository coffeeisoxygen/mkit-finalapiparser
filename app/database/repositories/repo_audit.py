"""Implementasi repository untuk AuditMixin.

AuditMixinRepository mengimplementasikan kontrak IAuditMixinRepo untuk operasi audit dan soft delete pada entity yang menggunakan AuditMixin.
"""

import uuid
from datetime import datetime
from typing import Any

from app.custom.exceptions.cst_exceptions import AuditMixinError
from app.database.interfaces.intf_audit import IAuditMixinRepo
from app.database.repositories.helpers import pk_for_query, to_uuid_str


class AuditMixinRepository(IAuditMixinRepo[Any]):
    """Generic repository for audit and soft delete operations on AuditMixin entities.

    Implements IAuditMixinRepo contract. All PK queries use pk_for_query for DB compatibility.
    Audit fields are always stored as string UUIDs.
    """

    def __init__(self, session: Any, entity_cls: type[Any]):
        """Initialize repository.

        Args:
            session: Async DB session.
            entity_cls: ORM model class using AuditMixin.
        """
        self.session = session
        self.entity_cls = entity_cls

    async def soft_delete(
        self, entity_id: uuid.UUID | str, actor_id: uuid.UUID | str
    ) -> None:
        """Mark record as soft deleted by actor_id.

        Args:
            entity_id: PK (UUID or str).
            actor_id: Actor performing delete (UUID or str).

        Raises:
            AuditMixinError: If entity not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if obj is None:
            raise AuditMixinError(f"Entity not found for soft_delete: {entity_id_pk}")
        obj.is_deleted_flag = True
        obj.deleted_by = to_uuid_str(actor_id)
        obj.deleted_at = datetime.now().astimezone()
        await self.session.commit()

    async def restore(self, entity_id: uuid.UUID | str) -> None:
        """Restore soft deleted record.

        Args:
            entity_id: PK (UUID or str).

        Raises:
            AuditMixinError: If entity not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if obj is None:
            raise AuditMixinError(f"Entity not found for restore: {entity_id_pk}")
        obj.is_deleted_flag = False
        obj.deleted_by = None
        obj.deleted_at = None
        await self.session.commit()

    async def get_audit_log(self, entity_id: uuid.UUID | str) -> dict:
        """Get audit log/history for entity as dict of audit fields.

        Args:
            entity_id: PK (UUID or str).

        Returns:
            dict: Audit fields for entity, or empty dict if not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if obj is None:
            return {}
        return {
            "created_by": obj.created_by,
            "created_at": obj.created_at,
            "updated_by": obj.updated_by,
            "updated_at": obj.updated_at,
            "deleted_by": obj.deleted_by,
            "deleted_at": obj.deleted_at,
        }
