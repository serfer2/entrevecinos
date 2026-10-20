import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from entrevecinos.domain.communities.entities import (
    Community,
    MembershipDetail,
    MembershipRole,
    MembershipStatus,
    MemberSummary,
    MyMembership,
    NewCommunity,
)
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


class UserSummaryResponse(BaseModel):
    """Esquema `UserSummary` del contrato."""

    id: uuid.UUID
    full_name: str
    avatar_url: str | None = None

    @classmethod
    def from_domain(cls, user: MemberSummary) -> "UserSummaryResponse":
        return cls(id=user.id, full_name=user.full_name)


class MembershipResponse(BaseModel):
    """Esquema `Membership` del contrato."""

    community_id: uuid.UUID
    user: UserSummaryResponse
    role: MembershipRole
    status: MembershipStatus
    reviewed_by: uuid.UUID | None
    requested_at: datetime
    reviewed_at: datetime | None
    joined_at: datetime | None

    @classmethod
    def from_domain(cls, detail: MembershipDetail) -> "MembershipResponse":
        membership = detail.membership
        return cls(
            community_id=membership.community_id,
            user=UserSummaryResponse.from_domain(detail.user),
            role=membership.role,
            status=membership.status,
            reviewed_by=membership.reviewed_by,
            requested_at=membership.requested_at,
            reviewed_at=membership.reviewed_at,
            joined_at=membership.joined_at,
        )


class MyMembershipResponse(BaseModel):
    """Esquema `MyMembership` del contrato."""

    community: CommunityResponse
    role: MembershipRole
    status: MembershipStatus
    requested_at: datetime
    joined_at: datetime | None

    @classmethod
    def from_domain(cls, mine: MyMembership) -> "MyMembershipResponse":
        return cls(
            community=CommunityResponse.from_domain(mine.community),
            role=mine.membership.role,
            status=mine.membership.status,
            requested_at=mine.membership.requested_at,
            joined_at=mine.membership.joined_at,
        )


class MyMembershipsResponse(BaseModel):
    items: list[MyMembershipResponse]


class MembershipErrorResponse(BaseModel):
    """Error de membresía con el estado actual (extensión del esquema `Error`)."""

    detail: str
    status: MembershipStatus
