import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entrevecinos.domain.communities.entities import (
    Community,
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.infrastructure.db.models import CommunityMembershipModel, CommunityModel


def community_to_domain(model: CommunityModel) -> Community:
    return Community(
        id=model.id,
        name=model.name,
        description=model.description,
        postal_code=model.postal_code,
        city=model.city,
        created_by=model.created_by,
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SqlAlchemyCommunityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, community: NewCommunity, admin_id: uuid.UUID) -> Community:
        model = CommunityModel(
            name=community.name,
            description=community.description,
            postal_code=community.postal_code,
            city=community.city,
            created_by=admin_id,
        )
        self._session.add(model)
        self._session.flush()
        now = self._session.scalar(select(func.now()))
        self._session.add(
            CommunityMembershipModel(
                community_id=model.id,
                user_id=admin_id,
                role=MembershipRole.COMMUNITY_ADMIN,
                status=MembershipStatus.APPROVED,
                reviewed_by=admin_id,
                reviewed_at=now,
                joined_at=now,
            )
        )
        self._session.flush()
        self._session.refresh(model)
        return community_to_domain(model)

    def get(self, community_id: uuid.UUID) -> Community | None:
        model = self._session.get(CommunityModel, community_id)
        if model is None or not model.is_active:
            return None
        return community_to_domain(model)
