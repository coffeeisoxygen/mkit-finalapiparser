"""Interface untuk repository AuditMixin.

Kontrak ini digunakan untuk operasi audit dan soft delete pada entity yang menggunakan AuditMixin.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic_extra_types.ulid import ULID

T = TypeVar("T")  # Entity type


class IAuditMixinRepo[T](ABC):
    """Interface repository untuk operasi audit dan soft delete.

    Method:
            soft_delete: Mark record as soft deleted.
            restore: Restore soft deleted record.
            get_audit_log: Get audit log for entity.
    """

    @abstractmethod
    async def soft_delete(self, entity_id: ULID | str, actor_id: ULID | str) -> None:
        """Mark record as soft deleted by actor_id."""
        pass

    @abstractmethod
    async def restore(self, entity_id: ULID | str, actor_id: ULID | str) -> None:
        """Restore soft deleted record by actor_id."""
        pass

    @abstractmethod
    async def get_audit_log(self, entity_id: ULID | str) -> list[Any]:
        """Get audit log/history for entity."""
        pass
