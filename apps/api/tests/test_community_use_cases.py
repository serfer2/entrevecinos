import dataclasses
import uuid

import pytest

from entrevecinos.application.communities.create_community import CreateCommunity
from entrevecinos.application.communities.get_community import GetCommunity
from entrevecinos.domain.communities.entities import (
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import CommunityNotFound
from tests.fakes import InMemoryCommunityRepository


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
