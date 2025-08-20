from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.interfaces.interface_auditlog import IAuditLogRepo
from app.models.db_audit import AuditLog


class LiteAuditLogRepo(IAuditLogRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self, description: dict | str, detail: dict | None = None
    ) -> AuditLog:
        """Create a new audit log entry.

        Args:
            description (dict | str): Deskripsi log.
            detail (dict | None): Detail tambahan.

        Returns:
            AuditLog: Instance log yang baru dibuat.
        """
        audit = AuditLog(description=description, detail=detail)
        self.session.add(audit)
        await self.session.flush()
        return audit
