from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.custom.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.models.member import Member


class MemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, member: Member):
        existing = await self.session.get(Member, member.memberid)
        if existing:
            raise EntityAlreadyExistsError(f"Member {member.memberid} already exists.")
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get(self, memberid: str):
        member = await self.session.get(Member, memberid)
        if not member:
            raise EntityNotFoundError(f"Member {memberid} not found.")
        return member

    async def update(self, memberid: str, **kwargs):
        stmt = update(Member).where(Member.memberid == memberid).values(**kwargs)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise EntityNotFoundError(f"Member {memberid} not found.")
        await self.session.commit()
        return await self.get(memberid)

    async def remove(self, memberid: str):
        stmt = delete(Member).where(Member.memberid == memberid)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise EntityNotFoundError(f"Member {memberid} not found.")
        await self.session.commit()

    async def all(self):
        result = await self.session.execute(select(Member))
        return result.scalars().all()
