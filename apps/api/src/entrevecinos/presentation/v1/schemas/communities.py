import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from entrevecinos.domain.communities.entities import Community, NewCommunity
from entrevecinos.presentation.v1.schemas.common import OptionalText, RequiredText


class CommunityCreateRequest(BaseModel):
    """Esquema `CommunityCreate` del contrato."""

    model_config = ConfigDict(extra="forbid")

    name: RequiredText(120)
    description: OptionalText(2000)
    postal_code: OptionalText(16)
    city: OptionalText(120)

    def to_domain(self) -> NewCommunity:
        return NewCommunity(
            name=self.name,
            description=self.description,
            postal_code=self.postal_code,
            city=self.city,
        )


class CommunityResponse(BaseModel):
    """Esquema `Community` del contrato."""

    id: uuid.UUID
    name: str
    description: str | None
    postal_code: str | None
    city: str | None
    created_by: uuid.UUID
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, community: Community) -> "CommunityResponse":
        return cls(
            id=community.id,
            name=community.name,
            description=community.description,
            postal_code=community.postal_code,
            city=community.city,
            created_by=community.created_by,
            is_active=community.is_active,
            created_at=community.created_at,
        )
