"""Implementasi repository untuk AuditMixin.

AuditMixinRepository mengimplementasikan kontrak IAuditMixinRepo untuk operasi audit dan soft delete pada entity yang menggunakan AuditMixin.
"""

import uuid
from datetime import datetime
from typing import Any

from app.custom.exceptions.cst_exceptions import AuditMixinError
from app.interfaces.intf_audit import IAuditMixinRepo


class AuditMixinRepository(IAuditMixinRepo[Any]):
    """Generic repository untuk operasi audit dan soft delete pada entity AuditMixin."""

    def __init__(self, session: Any, entity_cls: type[Any]):
        self.session = session
        self.entity_cls = entity_cls

    async def soft_delete(self, entity_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        obj = await self.session.get(self.entity_cls, entity_id)
        if obj is None:
            raise AuditMixinError(f"Entity not found for soft_delete: {entity_id}")
        obj.is_deleted_flag = True
        obj.deleted_by = actor_id
        obj.deleted_at = datetime.now().astimezone()
        await self.session.commit()

    async def restore(self, entity_id: uuid.UUID) -> None:
        obj = await self.session.get(self.entity_cls, entity_id)
        if obj is None:
            raise AuditMixinError(f"Entity not found for restore: {entity_id}")
        obj.is_deleted_flag = False
        obj.deleted_by = None
        obj.deleted_at = None
        await self.session.commit()

    async def get_audit_log(self, entity_id: uuid.UUID) -> dict:
        obj = await self.session.get(self.entity_cls, entity_id)
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
