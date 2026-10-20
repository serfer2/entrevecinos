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
from entrevecinos.domain.communities.errors import CommunityNotFound, MembershipAlreadyExists
from tests.fakes import InMemoryCommunityRepository, InMemoryMembershipRepository


def test_creator_becomes_approved_admin() -> None:
    repository = InMemoryCommunityRepository()
    creator = uuid.uuid4()

    community = CreateCommunity(repository).execute(
        NewCommunity(name="Los Olivos", city="Majadahonda"), creator_id=creator
    )

    assert community.created_by == creator
    membership = repository.memberships[(community.id, creator)]
    assert membership.role is MembershipRole.COMMUNITY_ADMIN
    assert membership.status is MembershipStatus.APPROVED
    assert membership.joined_at is not None


def test_get_returns_active_community() -> None:
    repository = InMemoryCommunityRepository()
    community = CreateCommunity(repository).execute(NewCommunity(name="X"), uuid.uuid4())

    assert GetCommunity(repository).execute(community.id) == community


def test_get_raises_not_found_for_missing_or_inactive() -> None:
    repository = InMemoryCommunityRepository()
    community = CreateCommunity(repository).execute(NewCommunity(name="X"), uuid.uuid4())
    repository.communities[community.id] = dataclasses.replace(community, is_active=False)

    with pytest.raises(CommunityNotFound):
        GetCommunity(repository).execute(community.id)
    with pytest.raises(CommunityNotFound):
        GetCommunity(repository).execute(uuid.uuid4())


def test_request_membership_creates_pending_member() -> None:
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    community = CreateCommunity(communities).execute(NewCommunity(name="X"), uuid.uuid4())
    user = uuid.uuid4()

    detail = RequestMembership(communities, memberships).execute(community.id, user)

    assert detail.membership.status is MembershipStatus.PENDING
    assert detail.membership.role is MembershipRole.MEMBER
    assert [m.community for m in ListMyMemberships(memberships).execute(user)] == [community]


@pytest.mark.parametrize("status", list(MembershipStatus))
def test_request_membership_rejects_any_existing_membership(status: MembershipStatus) -> None:
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    community = CreateCommunity(communities).execute(NewCommunity(name="X"), uuid.uuid4())
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
