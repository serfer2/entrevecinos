import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PlatformRole(StrEnum):
    USER = "user"
    PLATFORM_ADMIN = "platform_admin"


@dataclass(frozen=True, slots=True)
class NewUser:
    """Datos de un usuario que todavía no se ha guardado."""

    email: str
    full_name: str
    phone: str | None = None


@dataclass(frozen=True, slots=True)
class User:
    """Usuario registrado. Nunca contiene el hash de la contraseña."""

    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    platform_role: PlatformRole
    is_active: bool
    created_at: datetime
    deleted_at: datetime | None = None
