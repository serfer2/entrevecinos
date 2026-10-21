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
    email_verified_at: datetime | None = None

    @property
    def can_authenticate(self) -> bool:
        return self.is_active and self.deleted_at is None

    @property
    def email_verification_pending(self) -> bool:
        """Falta validar el correo. Un `platform_admin` no lo necesita para estar activo."""
        return (
            self.email_verified_at is None
            and self.platform_role != PlatformRole.PLATFORM_ADMIN
            and self.deleted_at is None
        )


@dataclass(frozen=True, slots=True)
class EmailVerification:
    """Enlace de validación pendiente de usar. No incluye el token: solo viaja por correo."""

    user_id: uuid.UUID
    expires_at: datetime
    created_at: datetime
