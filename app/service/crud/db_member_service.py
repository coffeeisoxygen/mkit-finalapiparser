from app.custom.exceptions import EntityAlreadyExistsError
from app.models.db_member import Member
from app.repositories.persistance import MemberRepository
from app.schemas.sch_member import MemberCreate, MemberPublic, MemberUpdate
from app.service.security import HasherService


class MemberService:
    def __init__(self, repository: MemberRepository):
        self.repository = repository

    async def create_new_member(self, member_data: MemberCreate) -> MemberPublic:
        """Logika bisnis untuk membuat member baru.

        Melakukan validasi duplikasi dan hashing password/pin.
        """
        # 1. Validasi bisnis: Cek duplikasi memberid secara proaktif
        existing_member = await self.repository.get_member_by_memberid(
            member_data.memberid
        )
        if existing_member:
            raise EntityAlreadyExistsError(
                f"Member with memberid '{member_data.memberid}' already exists."
            )

        # 2. Logika bisnis: Hashing password dan pin
        hashed_password = HasherService.hash_value(member_data.password)
        hashed_pin = HasherService.hash_value(member_data.pin)

        # 3. Konversi Pydantic model ke SQLAlchemy model (termasuk data hash)
        member_db = Member(
            memberid=member_data.memberid,
            name=member_data.name,
            ipaddress=str(member_data.ipaddress),
            report_url=str(member_data.report_url),
            hash_password=hashed_password,
            hash_pin=hashed_pin,
            is_active=member_data.is_active,
            allow_nosign=member_data.allow_nosign,
        )

        # 4. Panggil repository untuk menyimpan data ke database
        created_member = await self.repository.create_member(member_db)

        # 5. Konversi hasil dari SQLAlchemy model ke Pydantic model
        #    untuk dikembalikan ke API/pengguna.
        return MemberPublic.model_validate(created_member)

    async def get_member_by_memberid(self, memberid: str) -> MemberPublic | None:
        """Ambil member berdasarkan memberid dan konversi ke model publik."""
        member = await self.repository.get_member_by_memberid(memberid)
        if member:
            return MemberPublic.model_validate(member)
        return None

    async def get_list_member(self) -> list[MemberPublic]:
        """Ambil semua member dan konversi ke list model publik."""
        members = await self.repository.get_list_member()
        return [MemberPublic.model_validate(member) for member in members]

    async def update_member(
        self, memberid: str, member_data: MemberUpdate
    ) -> MemberPublic:
        """Logika bisnis untuk mengupdate member.
        Cek apakah member ada, konversi, update data, dan simpan.
        """
        # 1. Cek apakah member yang akan diupdate ada di database
        member_to_update = await self.repository.get_member_by_memberid(memberid)
        if not member_to_update:
            raise MemberNotFoundError(f"Member with memberid '{memberid}' not found.")

        # 2. Loop melalui data update Pydantic dan perbarui atribut
        #    hanya jika field-nya diberikan (tidak None).
        update_dict = member_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if key == "password":
                member_to_update.hash_password = hash_password(value)
            elif key == "pin":
                member_to_update.hash_pin = hash_pin(value)
            elif key == "ipaddress" or key == "report_url":
                setattr(member_to_update, key, str(value))
            else:
                setattr(member_to_update, key, value)

        # 3. Panggil repository untuk menyimpan perubahan
        updated_member = await self.repository.update_member(member_to_update)

        # 4. Konversi dan kembalikan model publik
        return MemberPublic.model_validate(updated_member)

    async def delete_member(self, memberid: str) -> None:
        """Logika bisnis untuk menghapus member."""
        # 1. Cek apakah member ada sebelum memanggil repository
        member_to_delete = await self.repository.get_member_by_memberid(memberid)
        if not member_to_delete:
            raise MemberNotFoundError(f"Member with memberid '{memberid}' not found.")

        # 2. Panggil repository untuk menghapus data
        await self.repository.delete_member(memberid)
