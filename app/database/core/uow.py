from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.mlogg import logger


class UnitOfWork:
    """Unit of Work pattern untuk handle transaksi multi-step.

    NOTE: Service / caller wajib commit() atau rollback().
    Kalau lupa, __aexit__ akan auto commit jika belum ada commit.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
        with logger.contextualize(uow="UnitOfWork"):
            logger.debug("UnitOfWork initialized")

    async def __aenter__(self):
        with logger.contextualize(uow="UnitOfWork"):
            logger.debug("__aenter__ called")
        return self

    async def commit(self):
        await self.session.commit()
        self._committed = True
        with logger.contextualize(uow="UnitOfWork"):
            logger.info("commit called")

    async def rollback(self):
        await self.session.rollback()
        with logger.contextualize(uow="UnitOfWork"):
            logger.info("rollback called")

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        with logger.contextualize(uow="UnitOfWork"):
            logger.debug("__aexit__ called", exc_type=exc_type, exc=exc)
        if exc_type:
            await self.rollback()
        elif not self._committed:
            await self.commit()
        with logger.contextualize(uow="UnitOfWork"):
            logger.debug("UnitOfWork exited")
