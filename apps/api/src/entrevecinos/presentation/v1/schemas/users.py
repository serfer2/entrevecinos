import uuid
from datetime import datetime

from pydantic import BaseModel

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
