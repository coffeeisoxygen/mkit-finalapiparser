from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    IPvAnyAddress,
    SecretStr,
    field_validator,
)


class MemberBase(BaseModel):
    """Base shared fields."""

    name: str = Field(..., description="Nama member", min_length=1, max_length=100)
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ipaddress: IPvAnyAddress = Field(
        ..., description="Alamat IP member", examples=["192.168.1.1"]
    )
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False,
        description="Apakah member diizinkan untuk hit tanpa Signature.",
    )


class MemberInDB(MemberBase):
    """Full member stored in DB."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "memberid": "M12345",
                "name": "John Doe",
                "pin": "123456",
                "password": "password123",
                "is_active": True,
                "ipaddress": "192.168.1.1",
                "report_url": "http://example.com/report",
                "allow_nosign": False,
            }
        },
    )

    memberid: str = Field(
        description="ID unik untuk member", min_length=5, pattern=r"^[a-zA-Z0-9]*$"
    )
    pin: SecretStr = Field(..., description="PIN untuk member", min_length=6)
    password: SecretStr = Field(..., description="Password untuk member", min_length=6)


class MemberPublic(MemberBase):
    """Response ke client, tanpa info sensitif."""

    memberid: str


class MemberCreate(BaseModel):
    """Admin create member."""

    name: str
    pin: str = Field(..., min_length=6, description="PIN untuk member")
    password: str = Field(..., min_length=6, description="Password untuk member")
    ipaddress: IPvAnyAddress
    report_url: AnyHttpUrl
    allow_nosign: bool = False


class MemberUpdate(BaseModel):
    """Admin update member (opsional semua)."""

    name: str | None = None
    pin: SecretStr | None = None
    password: SecretStr | None = None
    is_active: bool | None = None
    ipaddress: IPvAnyAddress | None = None
    report_url: AnyHttpUrl | None = None
    allow_nosign: bool | None = None

    @field_validator(
        "name", "pin", "password", "ipaddress", "report_url", mode="before"
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        # treat empty string, False, and None as None
        if value in (None, "", False):
            return None
        return value


class MemberDelete(BaseModel):
    """Admin delete member, cukup pakai id."""

    memberid: str
