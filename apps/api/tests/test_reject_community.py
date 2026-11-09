"""Caso de uso `RejectCommunity` (TK-112, HU-47) con repositorios en memoria."""

import uuid

import pytest

from entrevecinos.application.communities.approve_communities import RejectCommunity
from entrevecinos.domain.communities.entities import NewCommunity
from entrevecinos.domain.communities.errors import CommunityNotFound, CommunityNotPending
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole
from tests.fakes import InMemoryCommunityRepository
from tests.test_community_access import make_user


@pytest.fixture
def repository() -> InMemoryCommunityRepository:
    return InMemoryCommunityRepository()


def test_rejects_a_pending_community_and_its_membership(repository) -> None:
    creator = make_user()
    community = repository.add(NewCommunity(name="Los Pinos"), creator.id, is_active=False)

    rejected = RejectCommunity(repository).execute(
        make_user(PlatformRole.PLATFORM_ADMIN), community.id
    )

    assert rejected.id == community.id
    assert community.id not in repository.communities
    assert (community.id, creator.id) not in repository.memberships
    assert repository.has_pending(creator.id) is False


def test_active_community_is_not_rejected(repository) -> None:
    creator = make_user()
    community = repository.add(NewCommunity(name="Activa"), creator.id, is_active=True)

    with pytest.raises(CommunityNotPending):
        RejectCommunity(repository).execute(make_user(PlatformRole.PLATFORM_ADMIN), community.id)

    assert repository.get(community.id) == community


def test_unknown_community_is_not_found(repository) -> None:
    with pytest.raises(CommunityNotFound):
        RejectCommunity(repository).execute(make_user(PlatformRole.PLATFORM_ADMIN), uuid.uuid4())


def test_only_platform_admins_reject(repository) -> None:
    creator = make_user()
    community = repository.add(NewCommunity(name="Los Pinos"), creator.id, is_active=False)

    for user in (creator, make_user()):
        with pytest.raises(PermissionDenied):
            RejectCommunity(repository).execute(user, community.id)
    assert community.id in repository.communities
