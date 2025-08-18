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
    name: str = Field(..., description="Nama member", min_length=1, max_length=100)
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ipaddress: IPvAnyAddress = Field(
        ..., description="Alamat IP member", examples=["192.168.1.1"]
    )
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False, description="Apakah member diizinkan untuk hit tanpa Signature."
    )


class MemberInDB(MemberBase):
    memberid: str = Field(
        description="ID unik untuk member", min_length=5, pattern=r"^[a-zA-Z0-9]*$"
    )
    pin: SecretStr = Field(..., description="PIN untuk member", min_length=6)
    password: SecretStr = Field(..., description="Password untuk member", min_length=6)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_create(cls, memberid: str, data: "MemberCreate") -> "MemberInDB":
        return cls(
            memberid=memberid,
            name=data.name,
            pin=SecretStr(data.pin),
            password=SecretStr(data.password),
            ipaddress=data.ipaddress,
            report_url=data.report_url,
            allow_nosign=data.allow_nosign,
            is_active=True,
        )

    def update_from(self, patch: "MemberUpdate") -> None:
        data = patch.model_dump(exclude_unset=True)
        if "pin" in data and isinstance(data["pin"], str):
            data["pin"] = SecretStr(data["pin"])
        if "password" in data and isinstance(data["password"], str):
            data["password"] = SecretStr(data["password"])
        for k, v in data.items():
            setattr(self, k, v)


class MemberPublic(MemberBase):
    memberid: str


class MemberCreate(BaseModel):
    name: str
    pin: str = Field(..., min_length=6)
    password: str = Field(..., min_length=6)
    ipaddress: IPvAnyAddress
    report_url: AnyHttpUrl
    allow_nosign: bool = False


class MemberUpdate(BaseModel):
    name: str | None = None
    pin: str | SecretStr | None = None
    password: str | SecretStr | None = None
    is_active: bool | None = None
    ipaddress: IPvAnyAddress | None = None
    report_url: AnyHttpUrl | None = None
    allow_nosign: bool | None = None

    @field_validator(
        "name", "pin", "password", "ipaddress", "report_url", mode="before"
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if value in (None, "", False):
            return None
        return value


class MemberDelete(BaseModel):
    memberid: str
