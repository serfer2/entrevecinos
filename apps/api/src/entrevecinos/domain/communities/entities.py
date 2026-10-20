import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MembershipRole(StrEnum):
    MEMBER = "member"
    COMMUNITY_ADMIN = "community_admin"
    MODERATOR = "moderator"


class MembershipStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class NewCommunity:
    """Datos de una comunidad que todavía no se ha guardado."""

    name: str
    description: str | None = None
    postal_code: str | None = None
    city: str | None = None


@dataclass(frozen=True, slots=True)
class Community:
    id: uuid.UUID
    name: str
    description: str | None
    postal_code: str | None
    city: str | None
    created_by: uuid.UUID
    is_active: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Membership:
    """Pertenencia de un usuario a una comunidad."""

    community_id: uuid.UUID
    user_id: uuid.UUID
    role: MembershipRole
    status: MembershipStatus
    requested_at: datetime
    reviewed_by: uuid.UUID | None = None
    reviewed_at: datetime | None = None
    joined_at: datetime | None = None

    @property
    def is_approved(self) -> bool:
        return self.status is MembershipStatus.APPROVED


@dataclass(frozen=True, slots=True)
class MemberSummary:
    """Datos públicos mínimos de un miembro (esquema `UserSummary`)."""

    id: uuid.UUID
    full_name: str


@dataclass(frozen=True, slots=True)
class MembershipDetail:
    """Membresía con los datos públicos de su usuario."""

    membership: Membership
    user: MemberSummary


@dataclass(frozen=True, slots=True)
class MyMembership:
    """Membresía del usuario autenticado con su comunidad."""

    membership: Membership
    community: Community


@dataclass(frozen=True, slots=True)
class CommunitySearch:
    """Filtros de la búsqueda de comunidades; se combinan con AND."""

    text: str | None = None
    city: str | None = None
    postal_code: str | None = None
