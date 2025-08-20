"""AuditMixinRepository: Repository for audit and soft delete operations.

This module provides a generic repository class for handling audit fields and
soft delete logic for entities implementing the AuditMixin interface.

Features:
    - Soft delete and restore operations.
    - Audit log retrieval.
    - Designed for use with SQLAlchemy async sessions and SQLite UUID PKs.

Typical usage example:
    repo = AuditMixinRepository(session, MyEntity)
    await repo.soft_delete(entity_id, actor_id)
    await repo.restore(entity_id)
    audit_log = await repo.get_audit_log(entity_id)
"""

import uuid
from datetime import datetime
from typing import Any

from app.custom.exceptions.cst_exceptions import AuditMixinError
from app.database.interfaces.intf_audit import IAuditMixinRepo
from app.database.repositories.helpers_uuids import pk_for_query, to_uuid_str


class AuditMixinRepository(IAuditMixinRepo[Any]):
    """Generic repository for audit and soft delete operations on AuditMixin entities.

    This repository provides methods to soft delete, restore, and retrieve audit logs
    for entities that implement audit fields (created_by, updated_by, deleted_by, etc).

    Attributes:
        session: SQLAlchemy async session instance.
        entity_cls: ORM model class implementing AuditMixin.
    """

    def __init__(self, session: Any, entity_cls: type[Any]):
        """Initialize AuditMixinRepository.

        Args:
            session: SQLAlchemy async session.
            entity_cls: ORM model class.
        """
        self.session = session
        self.entity_cls = entity_cls

    async def soft_delete(
        self, entity_id: str | uuid.UUID, actor_id: str | uuid.UUID
    ) -> None:
        """Soft delete a record by setting is_deleted_flag and audit fields.

        Args:
            entity_id: Primary key of the entity to soft delete.
            actor_id: ID of the actor performing the deletion.

        Raises:
            AuditMixinError: If entity is not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if obj is None:
            raise AuditMixinError(f"Entity not found for soft_delete: {entity_id_pk}")

        obj.is_deleted_flag = True
        obj.deleted_by = to_uuid_str(actor_id)
        obj.deleted_at = datetime.now().astimezone()
        await self.session.commit()
        await self.session.refresh(obj)

    async def restore(self, entity_id: str | uuid.UUID) -> None:
        """Restore a soft deleted record by clearing is_deleted_flag and audit fields.

        Args:
            entity_id: Primary key of the entity to restore.

        Raises:
            AuditMixinError: If entity is not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if obj is None:
            raise AuditMixinError(f"Entity not found for restore: {entity_id_pk}")

        obj.is_deleted_flag = False
        obj.deleted_by = None
        obj.deleted_at = None
        await self.session.commit()
        await self.session.refresh(obj)

    async def get_audit_log(self, entity_id: str | uuid.UUID) -> dict:
        """Retrieve audit log fields for a given entity.

        Args:
            entity_id: Primary key of the entity.

        Returns:
            dict: Audit log fields (created_by, created_at, updated_by, updated_at, deleted_by, deleted_at).
            Returns empty dict if entity not found.
        """
        entity_id_pk = pk_for_query(entity_id)
        obj = await self.session.get(self.entity_cls, entity_id_pk)
        if not obj:
            return {}

        return {
            "created_by": obj.created_by,
            "created_at": obj.created_at,
            "updated_by": obj.updated_by,
            "updated_at": obj.updated_at,
            "deleted_by": obj.deleted_by,
            "deleted_at": obj.deleted_at,
        }
