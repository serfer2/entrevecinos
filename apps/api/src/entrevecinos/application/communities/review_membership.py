import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_ADMINS,
    CommunityAccess,
)
from entrevecinos.application.communities.ports import MembershipRepository
from entrevecinos.domain.communities.entities import MembershipDetail, MembershipStatus
from entrevecinos.domain.communities.errors import MembershipAlreadyReviewed, MembershipNotFound
from entrevecinos.domain.users.entities import User

REVIEW_RESULTS = frozenset({MembershipStatus.APPROVED, MembershipStatus.REJECTED})


class ReviewMembership:
    """Aprueba o rechaza una solicitud pendiente."""

    def __init__(self, access: CommunityAccess, memberships: MembershipRepository) -> None:
        self._access = access
        self._memberships = memberships

    def execute(
        self, reviewer: User, community_id: uuid.UUID, user_id: uuid.UUID, status: MembershipStatus
    ) -> MembershipDetail:
        if status not in REVIEW_RESULTS:
            raise ValueError(f"Not a review result: {status}")
        self._access.require_role(reviewer, community_id, COMMUNITY_ADMINS)
        membership = self._memberships.get(community_id, user_id)
        if membership is None:
            raise MembershipNotFound
        if membership.status is not MembershipStatus.PENDING:
            raise MembershipAlreadyReviewed
        return self._memberships.review(community_id, user_id, status, reviewer.id)
