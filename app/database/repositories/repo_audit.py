"""Implementasi repository untuk AuditMixin.

AuditMixinRepository mengimplementasikan kontrak IAuditMixinRepo untuk operasi audit dan soft delete pada entity yang menggunakan AuditMixin.
"""

from typing import Any

from pydantic_extra_types.ulid import ULID

from app.interfaces.intf_audit import IAuditMixinRepo


class AuditMixinRepository(IAuditMixinRepo[Any]):
    """Repository untuk operasi audit dan soft delete pada entity AuditMixin."""

    async def soft_delete(self, entity_id: ULID | str, actor_id: ULID | str) -> None:
        """Mark record as soft deleted by actor_id."""
        # TODO: Implement logic for soft delete
        pass

    async def restore(self, entity_id: ULID | str, actor_id: ULID | str) -> None:
        """Restore soft deleted record by actor_id."""
        # TODO: Implement logic for restore
        pass

    async def get_audit_log(self, entity_id: ULID | str) -> list[Any]:
        """Get audit log/history for entity."""
        # TODO: Implement logic for audit log retrieval
        return []
