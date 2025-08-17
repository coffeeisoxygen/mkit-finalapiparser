"""schema untuk Module , all thing related hanya di manage oleh admin."""

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, SecretStr, field_validator

from app.config import ProviderEnums


class ModuleBase(BaseModel):
    """Base schema for module."""

    provider: ProviderEnums
    name: str
    base_url: AnyHttpUrl | None = None
    is_active: bool = Field(default=True, description="Is the module active?")

    @field_validator("provider", mode="after")
    @classmethod
    def validate_provider(cls, value: str) -> ProviderEnums:
        for enum_member in ProviderEnums:
            if value.lower() == enum_member.value.lower():
                return enum_member
        raise ValueError(f"Invalid provider: {value!r}")


class ModuleInDB(ModuleBase):
    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "json_schema_extra": {
            "example": [
                {
                    "provider": "digipos",
                    "name": "XXXX",
                    "username": "XXXXX",
                    "msisdn": "62xxxxxxxx",
                    "pin": "123456",
                    "password": "pasxxxxx",
                    "email": "XXXX@gmail.com",
                    "is_active": "true",
                    "base_url": "http://10.0.0.3:10003",
                }
            ]
        },
    }
    moduleid: str = Field(
        description="ID unik untuk member", min_length=5, pattern=r"^[a-zA-Z0-9]*$"
    )
    username: SecretStr
    msisdn: SecretStr
    pin: SecretStr
    password: SecretStr
    email: EmailStr | None = None
    is_active: bool = True


class ModuleCreate(BaseModel):
    """Create module schema."""

    provider: ProviderEnums
    name: str
    base_url: AnyHttpUrl
    username: SecretStr
    msisdn: SecretStr
    pin: SecretStr
    password: SecretStr
    email: EmailStr | None = None


class ModulePublic(BaseModel):
    moduleid: str


class ModuleUpdate(BaseModel):
    moduleid: str | None = None
    provider: ProviderEnums | None = None
    name: str | None = None
    base_url: str | None = None
    username: SecretStr | None = None
    msisdn: SecretStr | None = None
    pin: SecretStr | None = None
    password: SecretStr | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class ModuleDelete(BaseModel):
    moduleid: str
