from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.mlogg import logger
from app.mlogg.utils import logger_wraps


class UnitOfWork:
    """Unit of Work pattern untuk handle transaksi multi-step.

    NOTE: Service / caller wajib commit() atau rollback().
    Kalau lupa, __aexit__ akan auto commit jika belum ada commit.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
        self.log = logger.bind(uow=self.__class__.__name__)
        self.log.info("UnitOfWork initialized")

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def __aenter__(self):
        return self

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def commit(self):
        await self.session.commit()
        self._committed = True

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def rollback(self):
        await self.session.rollback()

    @logger_wraps(entry=True, exit=True, level="INFO")
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        if exc_type:
            # ada exception -> rollback
            await self.rollback()
        elif not self._committed:
            # auto commit jika belum ada commit eksplisit
            await self.commit()
        self.log.info("UnitOfWork exited")
