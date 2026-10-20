import uuid
from typing import Protocol

from entrevecinos.domain.communities.entities import Community, NewCommunity


class CommunityRepository(Protocol):
    def add(self, community: NewCommunity, admin_id: uuid.UUID) -> Community:
        """Guarda la comunidad y la membresía `community_admin`/`approved` de `admin_id`."""
        ...

    def get(self, community_id: uuid.UUID) -> Community | None:
        """Comunidad activa, o `None` si no existe o está desactivada."""
        ...
