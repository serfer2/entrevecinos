from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from entrevecinos.presentation.v1.schemas.users import UserResponse

FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[EmailStr, Field(max_length=320)]
    password: Annotated[str, Field(min_length=12, max_length=128)]
    full_name: FullName
    phone: Annotated[str | None, Field(max_length=32)] = None

    @field_validator("phone", mode="before")
    @classmethod
    def blank_phone_is_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int
    user: UserResponse
