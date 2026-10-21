import uuid

from sqlalchemy import exists, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import (
    Community,
    CommunitySearch,
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import PendingCommunityExists
from entrevecinos.infrastructure.db.models import CommunityMembershipModel, CommunityModel
from entrevecinos.infrastructure.db.text_search import contains_text, starts_with_text


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

    def add(self, community: NewCommunity, admin_id: uuid.UUID, is_active: bool) -> Community:
        model = CommunityModel(
            name=community.name,
            description=community.description,
            postal_code=community.postal_code,
            city=community.city,
            created_by=admin_id,
            is_active=is_active,
        )
        try:
            # Savepoint: si otra petición creó a la vez una comunidad pendiente, la sesión sigue
            # usable.
            with self._session.begin_nested():
                self._session.add(model)
        except IntegrityError as error:
            if "uq_community_one_pending_per_creator" not in str(error.orig):
                raise
            raise PendingCommunityExists from error
        # statement_timestamp(): hora real del cambio, no la del inicio de la transacción.
        now = self._session.scalar(select(func.statement_timestamp()))
        self._session.add(
            CommunityMembershipModel(
                community_id=model.id,
                user_id=admin_id,
                role=MembershipRole.COMMUNITY_ADMIN,
                status=MembershipStatus.APPROVED,
                requested_at=now,
                reviewed_by=admin_id,
                reviewed_at=now,
                joined_at=now,
            )
        )
        self._session.flush()
        self._session.refresh(model)
        return community_to_domain(model)

    def has_pending(self, created_by: uuid.UUID) -> bool:
        return bool(
            self._session.scalar(
                select(
                    exists().where(
                        CommunityModel.created_by == created_by, CommunityModel.is_active.is_(False)
                    )
                )
            )
        )

    def get(self, community_id: uuid.UUID) -> Community | None:
        model = self._session.get(CommunityModel, community_id)
        if model is None or not model.is_active:
            return None
        return community_to_domain(model)

    def search(self, filters: CommunitySearch, page: PageRequest) -> PageResult[Community]:
        conditions = [CommunityModel.is_active.is_(True)]
        if filters.text:
            conditions.append(
                or_(
                    contains_text(CommunityModel.name, filters.text),
                    contains_text(CommunityModel.description, filters.text),
                )
            )
        if filters.city:
            conditions.append(contains_text(CommunityModel.city, filters.city))
        if filters.postal_code:
            conditions.append(starts_with_text(CommunityModel.postal_code, filters.postal_code))

        total = self._session.scalar(
            select(func.count()).select_from(CommunityModel).where(*conditions)
        )
        models = self._session.scalars(
            select(CommunityModel)
            .where(*conditions)
            .order_by(CommunityModel.name, CommunityModel.created_at, CommunityModel.id)
            .offset(page.offset)
            .limit(page.page_size)
        )
        return PageResult(items=[community_to_domain(m) for m in models], total=total or 0)

    def list_all(self, is_active: bool | None, page: PageRequest) -> PageResult[Community]:
        conditions = [] if is_active is None else [CommunityModel.is_active.is_(is_active)]
        total = self._session.scalar(
            select(func.count()).select_from(CommunityModel).where(*conditions)
        )
        models = self._session.scalars(
            select(CommunityModel)
            .where(*conditions)
            .order_by(CommunityModel.created_at, CommunityModel.id)
            .offset(page.offset)
            .limit(page.page_size)
        )
        return PageResult(items=[community_to_domain(m) for m in models], total=total or 0)

    def activate(self, community_id: uuid.UUID) -> Community | None:
        model = self._session.get(CommunityModel, community_id)
        if model is None:
            return None
        model.is_active = True
        self._session.flush()
        self._session.refresh(model)
        return community_to_domain(model)
