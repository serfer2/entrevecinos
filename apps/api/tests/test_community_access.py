import dataclasses
import uuid
from datetime import UTC, datetime

import pytest

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_ADMINS,
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.domain.communities.entities import (
    Membership,
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import CommunityNotFound, MembershipNotApproved
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole, User
from tests.fakes import InMemoryCommunityRepository, InMemoryMembershipRepository


def make_user(role: PlatformRole = PlatformRole.USER) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4()}@example.com",
        full_name="Vecino",
        phone=None,
        platform_role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def setup():
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    admin = make_user()
    community = communities.add(NewCommunity(name="X"), admin.id)
    return CommunityAccess(communities, memberships), memberships, community, admin


def add_membership(memberships, community, user, status, role=MembershipRole.MEMBER):
    memberships.memberships[(community.id, user.id)] = Membership(
        community_id=community.id,
        user_id=user.id,
        role=role,
        status=status,
        requested_at=datetime.now(UTC),
    )


def test_approved_member_passes(setup) -> None:
    access, memberships, community, _ = setup
    user = make_user()
    add_membership(memberships, community, user, MembershipStatus.APPROVED)

    assert access.require_member(user, community.id).user_id == user.id


@pytest.mark.parametrize(
    "status", [MembershipStatus.PENDING, MembershipStatus.REJECTED, MembershipStatus.BLOCKED]
)
def test_not_approved_member_is_rejected_with_status(setup, status) -> None:
    access, memberships, community, _ = setup
    user = make_user()
    add_membership(memberships, community, user, status)

    with pytest.raises(MembershipNotApproved) as error:
        access.require_member(user, community.id)
    assert error.value.status is status


def test_user_without_membership_is_denied(setup) -> None:
    access, _, community, _ = setup

    with pytest.raises(PermissionDenied) as error:
        access.require_member(make_user(), community.id)
    assert not isinstance(error.value, MembershipNotApproved)


def test_missing_community_is_not_found_first(setup) -> None:
    access, *_ = setup

    with pytest.raises(CommunityNotFound):
        access.require_member(make_user(), uuid.uuid4())


def test_platform_admin_always_passes(setup) -> None:
    access, _, community, _ = setup
    platform_admin = make_user(PlatformRole.PLATFORM_ADMIN)

    assert access.require_member(platform_admin, community.id) is None
    assert access.require_role(platform_admin, community.id, COMMUNITY_ADMINS) is None


def test_require_role(setup) -> None:
    access, memberships, community, admin = setup
    member, moderator, pending_admin = make_user(), make_user(), make_user()
    add_membership(memberships, community, member, MembershipStatus.APPROVED)
    add_membership(
        memberships, community, moderator, MembershipStatus.APPROVED, MembershipRole.MODERATOR
    )
    add_membership(
        memberships,
        community,
        pending_admin,
        MembershipStatus.PENDING,
        MembershipRole.COMMUNITY_ADMIN,
    )

    assert access.require_role(admin, community.id, COMMUNITY_ADMINS).user_id == admin.id
    assert access.has_role(moderator, community.id, COMMUNITY_MANAGERS)
    assert not access.has_role(moderator, community.id, COMMUNITY_ADMINS)
    for user in (member, pending_admin, make_user()):
        with pytest.raises(PermissionDenied):
            access.require_role(user, community.id, COMMUNITY_MANAGERS)


def test_inactive_community_is_not_found(setup) -> None:
    access, memberships, community, admin = setup
    memberships.communities.communities[community.id] = dataclasses.replace(
        community, is_active=False
    )

    with pytest.raises(CommunityNotFound):
        access.require_role(admin, community.id, COMMUNITY_ADMINS)
