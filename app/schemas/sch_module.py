from enum import StrEnum

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)


class ProviderEnums(StrEnum):
    DIGIPOS = "DIGIPOS"
    ISIMPLE = "ISIMPLE"


class ModuleBase(BaseModel):
    name: str = Field(..., description="Nama module", min_length=1, max_length=100)
    provider: ProviderEnums = Field(..., description="Provider module")
    username: str = Field(..., description="Username untuk module")
    msisdn: str = Field(..., description="MSISDN (nomor telepon) module")
    email: EmailStr = Field(..., description="Email kontak module")
    base_url: AnyHttpUrl = Field(..., description="Base URL API module")
    is_active: bool = Field(default=True, description="Status aktif module")


class ModuleInDB(ModuleBase):
    moduleid: str = Field(
        description="ID unik untuk module", min_length=5, pattern=r"^[a-zA-Z0-9]*$"
    )
    pin: SecretStr = Field(..., description="PIN untuk module", min_length=6)
    password: SecretStr = Field(..., description="Password untuk module", min_length=6)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_create(cls, moduleid: str, data: "ModuleCreate") -> "ModuleInDB":
        return cls(
            moduleid=moduleid,
            name=data.name,
            provider=data.provider,
            username=data.username,
            msisdn=data.msisdn,
            pin=SecretStr(data.pin),
            password=SecretStr(data.password),
            email=data.email,
            base_url=data.base_url,
            is_active=True,
        )

    def update_from(self, patch: "ModuleUpdate") -> None:
        data = patch.model_dump(exclude_unset=True)
        if "pin" in data and isinstance(data["pin"], str):
            data["pin"] = SecretStr(data["pin"])
        if "password" in data and isinstance(data["password"], str):
            data["password"] = SecretStr(data["password"])
        for k, v in data.items():
            setattr(self, k, v)


class ModulePublic(ModuleBase):
    moduleid: str


class ModuleCreate(BaseModel):
    name: str
    provider: ProviderEnums = Field(..., description="Provider module")
    username: str
    msisdn: str
    pin: str = Field(..., min_length=6)
    password: str = Field(..., min_length=6)
    email: EmailStr
    base_url: AnyHttpUrl

    model_config = ConfigDict(extra="forbid", use_enum_values=False)


class ModuleUpdate(BaseModel):
    name: str | None = None
    provider: ProviderEnums | None = None
    username: str | None = None
    msisdn: str | None = None
    pin: str | SecretStr | None = None
    password: str | SecretStr | None = None
    email: EmailStr | None = None
    base_url: AnyHttpUrl | None = None
    is_active: bool | None = None

    @field_validator(
        "name",
        "pin",
        "password",
        "username",
        "msisdn",
        "email",
        "base_url",
        mode="before",
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if value in (None, "", False):
            return None
        return value


class ModuleDelete(BaseModel):
    moduleid: str
