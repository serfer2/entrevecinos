import dataclasses
import uuid

import pytest

from entrevecinos.application.communities.create_community import CreateCommunity
from entrevecinos.application.communities.get_community import GetCommunity
from entrevecinos.application.communities.list_my_memberships import ListMyMemberships
from entrevecinos.application.communities.request_membership import RequestMembership
from entrevecinos.domain.communities.entities import (
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import (
    CommunityNotFound,
    MembershipAlreadyExists,
    PendingCommunityExists,
)
from entrevecinos.domain.users.entities import PlatformRole
from tests.fakes import InMemoryCommunityRepository, InMemoryMembershipRepository
from tests.test_community_access import make_user


def test_creator_becomes_approved_admin_of_a_pending_community() -> None:
    repository = InMemoryCommunityRepository()
    creator = make_user()

    community = CreateCommunity(repository).execute(
        NewCommunity(name="Los Olivos", city="Majadahonda"), creator=creator
    )

    assert community.created_by == creator.id
    assert community.is_active is False
    membership = repository.memberships[(community.id, creator.id)]
    assert membership.role is MembershipRole.COMMUNITY_ADMIN
    assert membership.status is MembershipStatus.APPROVED
    assert membership.joined_at is not None


def test_platform_admin_creates_an_active_community() -> None:
    repository = InMemoryCommunityRepository()
    creator = make_user(PlatformRole.PLATFORM_ADMIN)

    community = CreateCommunity(repository).execute(NewCommunity(name="X"), creator=creator)

    assert community.is_active is True
    assert repository.memberships[(community.id, creator.id)].role is MembershipRole.COMMUNITY_ADMIN


def test_only_one_pending_community_per_creator() -> None:
    repository = InMemoryCommunityRepository()
    creator = make_user()
    create = CreateCommunity(repository)
    pending = create.execute(NewCommunity(name="Primera"), creator=creator)

    with pytest.raises(PendingCommunityExists):
        create.execute(NewCommunity(name="Segunda"), creator=creator)

    repository.activate(pending.id)
    assert create.execute(NewCommunity(name="Segunda"), creator=creator).is_active is False


def test_platform_admin_is_not_limited_by_pending_communities() -> None:
    repository = InMemoryCommunityRepository()
    creator = make_user(PlatformRole.PLATFORM_ADMIN)
    create = CreateCommunity(repository)

    create.execute(NewCommunity(name="Primera"), creator=creator)

    assert create.execute(NewCommunity(name="Segunda"), creator=creator).is_active is True


def test_get_returns_active_community() -> None:
    repository = InMemoryCommunityRepository()
    community = repository.add(NewCommunity(name="X"), uuid.uuid4(), is_active=True)

    assert GetCommunity(repository).execute(community.id) == community


def test_get_raises_not_found_for_missing_or_inactive() -> None:
    repository = InMemoryCommunityRepository()
    community = repository.add(NewCommunity(name="X"), uuid.uuid4(), is_active=True)
    repository.communities[community.id] = dataclasses.replace(community, is_active=False)

    with pytest.raises(CommunityNotFound):
        GetCommunity(repository).execute(community.id)
    with pytest.raises(CommunityNotFound):
        GetCommunity(repository).execute(uuid.uuid4())


def test_request_membership_creates_pending_member() -> None:
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    community = communities.add(NewCommunity(name="X"), uuid.uuid4(), is_active=True)
    user = uuid.uuid4()

    detail = RequestMembership(communities, memberships).execute(community.id, user)

    assert detail.membership.status is MembershipStatus.PENDING
    assert detail.membership.role is MembershipRole.MEMBER
    assert [m.community for m in ListMyMemberships(memberships).execute(user)] == [community]


@pytest.mark.parametrize("status", list(MembershipStatus))
def test_request_membership_rejects_any_existing_membership(status: MembershipStatus) -> None:
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    community = communities.add(NewCommunity(name="X"), uuid.uuid4(), is_active=True)
    user = uuid.uuid4()
    RequestMembership(communities, memberships).execute(community.id, user)
    key = (community.id, user)
    memberships.memberships[key] = dataclasses.replace(memberships.memberships[key], status=status)

    with pytest.raises(MembershipAlreadyExists) as error:
        RequestMembership(communities, memberships).execute(community.id, user)
    assert error.value.status is status


def test_request_membership_requires_existing_community() -> None:
    communities = InMemoryCommunityRepository()

    with pytest.raises(CommunityNotFound):
        RequestMembership(communities, InMemoryMembershipRepository(communities)).execute(
            uuid.uuid4(), uuid.uuid4()
        )
