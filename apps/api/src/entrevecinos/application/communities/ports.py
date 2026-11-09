import uuid
from typing import Protocol

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import (
    Community,
    CommunitySearch,
    Membership,
    MembershipDetail,
    MembershipRole,
    MembershipStatus,
    MyMembership,
    NewCommunity,
)
from entrevecinos.domain.users.entities import User


class CommunityRepository(Protocol):
    def add(self, community: NewCommunity, admin_id: uuid.UUID, is_active: bool) -> Community:
        """Guarda la comunidad y la membresía `community_admin`/`approved` de `admin_id`.

        En el MVP, una comunidad inactiva es una comunidad pendiente de aprobación. Lanza
        `PendingCommunityExists` si `admin_id` ya tiene una pendiente (también en una carrera).
        """
        ...

    def has_pending(self, created_by: uuid.UUID) -> bool:
        """`True` si el usuario creó una comunidad que sigue pendiente de aprobación."""
        ...

    def get(self, community_id: uuid.UUID) -> Community | None:
        """Comunidad activa, o `None` si no existe o está desactivada."""
        ...

    def search(self, filters: CommunitySearch, page: PageRequest) -> PageResult[Community]:
        """Comunidades activas que cumplen los filtros, ordenadas por nombre."""
        ...

    def list_all(self, is_active: bool | None, page: PageRequest) -> PageResult[Community]:
        """Todas las comunidades (o las de `is_active`), de la más antigua a la más reciente."""
        ...

    def activate(self, community_id: uuid.UUID) -> Community | None:
        """Activa la comunidad (esté o no activa), o `None` si no existe."""
        ...

    def delete_pending(self, community_id: uuid.UUID) -> Community | None:
        """Elimina una comunidad pendiente y, en cascada, sus membresías; devuelve la eliminada.

        `None` si no existe. Lanza `CommunityNotPending` si está activa. Bloquea la fila para que
        un rechazo y una aprobación simultáneos no se pisen.
        """
        ...


class MembershipRepository(Protocol):
    def get(self, community_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None: ...

    def add_request(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail:
        """Crea una membresía `pending`/`member`.

        Lanza `MembershipAlreadyExists` si ya existe una (también en una carrera).
        """
        ...

    def get_detail(
        self, community_id: uuid.UUID, user_id: uuid.UUID
    ) -> MembershipDetail | None: ...

    def list_for_community(
        self, community_id: uuid.UUID, status: MembershipStatus | None, page: PageRequest
    ) -> PageResult[MembershipDetail]:
        """Con `status`, de la solicitud más antigua a la más reciente; sin él, por estado
        (pendientes, miembros, bloqueados, rechazados) y nombre."""
        ...

    def count_admins(self, community_id: uuid.UUID, lock: bool = False) -> int:
        """Administradores de la comunidad con membresía aprobada.

        Con `lock`, bloquea sus filas hasta el final de la transacción para que dos cambios
        simultáneos no dejen la comunidad sin administrador.
        """
        ...

    def set_role(
        self, community_id: uuid.UUID, user_id: uuid.UUID, role: MembershipRole
    ) -> MembershipDetail:
        """Fija el rol de una membresía existente sin tocar su estado ni su revisión."""
        ...

    def list_admin_recipients(self, community_id: uuid.UUID) -> list[User]:
        """Administradores aprobados de la comunidad con la cuenta activa, por nombre (TK-106)."""
        ...

    def delete(self, community_id: uuid.UUID, user_id: uuid.UUID) -> None: ...

    def review(
        self,
        community_id: uuid.UUID,
        user_id: uuid.UUID,
        status: MembershipStatus,
        reviewer_id: uuid.UUID,
    ) -> MembershipDetail:
        """Fija el estado y `reviewed_by`/`reviewed_at` (y `joined_at` la primera aprobación)."""
        ...

    def list_for_user(
        self, user_id: uuid.UUID, status: MembershipStatus | None = None
    ) -> list[MyMembership]:
        """Membresías del usuario, de la más reciente a la más antigua."""
        ...
