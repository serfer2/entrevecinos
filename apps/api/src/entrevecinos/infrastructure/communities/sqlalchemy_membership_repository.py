import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import (
    Membership,
    MembershipDetail,
    MembershipRole,
    MembershipStatus,
    MemberSummary,
    MyMembership,
)
from entrevecinos.domain.communities.errors import MembershipAlreadyExists
from entrevecinos.infrastructure.communities.sqlalchemy_community_repository import (
    community_to_domain,
)
from entrevecinos.infrastructure.db.models import (
    CommunityMembershipModel,
    CommunityModel,
    UserModel,
)


def membership_to_domain(model: CommunityMembershipModel) -> Membership:
    return Membership(
        community_id=model.community_id,
        user_id=model.user_id,
        role=MembershipRole(model.role),
        status=MembershipStatus(model.status),
        requested_at=model.requested_at,
        reviewed_by=model.reviewed_by,
        reviewed_at=model.reviewed_at,
        joined_at=model.joined_at,
    )


def detail_to_domain(model: CommunityMembershipModel, user: UserModel) -> MembershipDetail:
    return MembershipDetail(
        membership=membership_to_domain(model),
        user=MemberSummary(id=user.id, full_name=user.full_name),
    )


class SqlAlchemyMembershipRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _model(
        self, community_id: uuid.UUID, user_id: uuid.UUID
    ) -> CommunityMembershipModel | None:
        return self._session.get(CommunityMembershipModel, (community_id, user_id))

    def get(self, community_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None:
        model = self._model(community_id, user_id)
        return membership_to_domain(model) if model else None

    def add_request(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail:
        model = CommunityMembershipModel(
            community_id=community_id,
            user_id=user_id,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING,
            requested_at=func.statement_timestamp(),
        )
        try:
            # Savepoint: si otra petición creó la membresía a la vez, la sesión sigue usable.
            with self._session.begin_nested():
                self._session.add(model)
        except IntegrityError as error:
            if "pk_community_membership" not in str(error.orig):
                raise
            existing = self._model(community_id, user_id)
            raise MembershipAlreadyExists(MembershipStatus(existing.status)) from error
        self._session.refresh(model)
        return detail_to_domain(model, self._session.get_one(UserModel, user_id))

    def get_detail(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail | None:
        model = self._model(community_id, user_id)
        return detail_to_domain(model, self._session.get_one(UserModel, user_id)) if model else None

    def list_for_community(
        self, community_id: uuid.UUID, status: MembershipStatus | None, page: PageRequest
    ) -> PageResult[MembershipDetail]:
        conditions = [CommunityMembershipModel.community_id == community_id]
        if status is not None:
            conditions.append(CommunityMembershipModel.status == status)
        total = self._session.scalar(
            select(func.count()).select_from(CommunityMembershipModel).where(*conditions)
        )
        rows = self._session.execute(
            select(CommunityMembershipModel, UserModel)
            .join(UserModel, UserModel.id == CommunityMembershipModel.user_id)
            .where(*conditions)
            .order_by(CommunityMembershipModel.requested_at, CommunityMembershipModel.user_id)
            .offset(page.offset)
            .limit(page.page_size)
        )
        return PageResult(items=[detail_to_domain(m, u) for m, u in rows], total=total or 0)

    def review(
        self,
        community_id: uuid.UUID,
        user_id: uuid.UUID,
        status: MembershipStatus,
        reviewer_id: uuid.UUID,
    ) -> MembershipDetail:
        model = self._session.get_one(CommunityMembershipModel, (community_id, user_id))
        now = self._session.scalar(select(func.statement_timestamp()))
        model.status = status
        model.reviewed_by = reviewer_id
        model.reviewed_at = now
        if status is MembershipStatus.APPROVED:
            model.joined_at = now
        self._session.flush()
        self._session.refresh(model)
        return detail_to_domain(model, self._session.get_one(UserModel, user_id))

    def list_for_user(
        self, user_id: uuid.UUID, status: MembershipStatus | None = None
    ) -> list[MyMembership]:
        query = (
            select(CommunityMembershipModel, CommunityModel)
            .join(CommunityModel, CommunityModel.id == CommunityMembershipModel.community_id)
            .where(
                CommunityMembershipModel.user_id == user_id,
                # Una comunidad desactivada solo se muestra a quien ya era miembro.
                or_(
                    CommunityModel.is_active.is_(True),
                    CommunityMembershipModel.status == MembershipStatus.APPROVED,
                ),
            )
            .order_by(
                CommunityMembershipModel.requested_at.desc(), CommunityMembershipModel.community_id
            )
        )
        if status is not None:
            query = query.where(CommunityMembershipModel.status == status)
        return [
            MyMembership(membership=membership_to_domain(m), community=community_to_domain(c))
            for m, c in self._session.execute(query)
        ]
