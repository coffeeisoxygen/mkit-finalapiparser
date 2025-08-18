# app_crud.py
from sqlalchemy.ext.asyncio import AsyncSession


class AppCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit_refresh(self, entity):  # noqa: ANN001
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def commit(self):
        await self.session.commit()
