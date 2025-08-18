from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_member import Member


class MemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_member_by_memberid(self, memberid: str) -> Member | None:
        """Ambil objek Member SQLA dari database berdasarkan memberid."""
        stmt = select(Member).where(Member.memberid == memberid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_member(self, member: Member) -> Member:
        """Simpan objek Member SQLA yang sudah lengkap ke database."""
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def get_member_by_id(self, id: int) -> Member | None:
        """Ambil objek Member SQLA dari database berdasarkan id."""
        stmt = select(Member).where(Member.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_member(self) -> Sequence[Member]:
        """Ambil semua objek Member SQLA dari database."""
        stmt = select(Member)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_member(self, member: Member) -> Member | None:
        """Update objek Member di database."""
        stmt = select(Member).where(Member.id == member.id)
        result = await self.session.execute(stmt)
        existing_member = result.scalar_one_or_none()
        if not existing_member:
            return None

        for key, value in member.__dict__.items():
            if key in existing_member.__dict__ and key != "_sa_instance_state":
                setattr(existing_member, key, value)

        await self.session.commit()
        await self.session.refresh(existing_member)
        return existing_member

    async def delete_member(self, memberid: str) -> None:
        """Hapus objek Member dari database berdasarkan memberid."""
        stmt = select(Member).where(Member.memberid == memberid)
        result = await self.session.execute(stmt)
        existing_member = result.scalar_one_or_none()
        if existing_member:
            await self.session.delete(existing_member)
            await self.session.commit()
