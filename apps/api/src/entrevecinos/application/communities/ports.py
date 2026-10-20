import uuid
from typing import Protocol

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import (
    Community,
    CommunitySearch,
    Membership,
    MembershipDetail,
    MembershipStatus,
    MyMembership,
    NewCommunity,
)


class CommunityRepository(Protocol):
    def add(self, community: NewCommunity, admin_id: uuid.UUID) -> Community:
        """Guarda la comunidad y la membresía `community_admin`/`approved` de `admin_id`."""
        ...

    def get(self, community_id: uuid.UUID) -> Community | None:
        """Comunidad activa, o `None` si no existe o está desactivada."""
        ...

    def search(self, filters: CommunitySearch, page: PageRequest) -> PageResult[Community]:
        """Comunidades activas que cumplen los filtros, ordenadas por nombre."""
        ...


class MembershipRepository(Protocol):
    def get(self, community_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None: ...

    def add_request(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail:
        """Crea una membresía `pending`/`member`.

        Lanza `MembershipAlreadyExists` si ya existe una (también en una carrera).
        """
        ...

    def list_for_user(
        self, user_id: uuid.UUID, status: MembershipStatus | None = None
    ) -> list[MyMembership]:
        """Membresías del usuario, de la más reciente a la más antigua."""
        ...
