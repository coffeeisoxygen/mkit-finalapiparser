from pydantic import AnyHttpUrl, BaseModel, Field, IPvAnyAddress


# Base schema: shared fields
class MemberBase(BaseModel):
    memberid: str = Field(
        ...,
        description="ID unik member, ini untuk transaksi bukan , DB Sequence",
        min_length=1,
        max_length=10,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    name: str = Field(..., description="Nama member", min_length=1, max_length=100)
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ipaddress: IPvAnyAddress = Field(..., description="Alamat IP member")
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False, description="Apakah member bisa hit tanpa signature"
    )
    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "populate_by_name": True,
    }


# Schema untuk simpan di DB
class MemberInDB(MemberBase):
    password: str
    pin: str


# Schema untuk create
class MemberCreate(MemberBase):
    password: str
    pin: str


# Schema untuk response publik
class MemberPublic(MemberBase):
    id: int
    pass


# Schema untuk update (semua optional)
class MemberUpdate(BaseModel):
    memberid: str | None = None
    name: str | None = None
    password: str | None = None
    pin: str | None = None
    is_active: bool | None = None
    ipaddress: IPvAnyAddress | None = None
    report_url: AnyHttpUrl | None = None
    allow_nosign: bool | None = None

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "populate_by_name": True,
    }
