import uuid
from datetime import datetime
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from entrevecinos.domain.users.entities import PlatformRole, User


class UserResponse(BaseModel):
    """Esquema `User` del contrato: nunca incluye el hash de la contraseña."""

    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    avatar_url: str | None = None
    platform_role: PlatformRole
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            platform_role=user.platform_role,
            is_active=user.is_active,
            created_at=user.created_at,
        )


PHONE_PATTERN = r"^\+?[0-9 ()-]{6,32}$"


class UserUpdateRequest(BaseModel):
    """Subconjunto implementado de `UserUpdate`: avatar y contraseña llegarán en otros tickets."""

    model_config = ConfigDict(extra="forbid")

    # `None` solo como «no enviado»: un `null` explícito lo rechaza full_name_is_not_null.
    full_name: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
        | None
    ) = None
    phone: Annotated[str | None, Field(max_length=32, pattern=PHONE_PATTERN)] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def full_name_is_not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("full_name cannot be null")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def blank_phone_is_none(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self
