"""Caso de uso `ChangeMembershipRole` (TK-109, HU-45) con repositorios en memoria."""

import uuid

import pytest

from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.communities.review_membership import ChangeMembershipRole
from entrevecinos.domain.communities.entities import (
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import (
    CommunityNotFound,
    MembershipChangeRejected,
    MembershipNotFound,
)
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole
from tests.fakes import InMemoryCommunityRepository, InMemoryMembershipRepository
from tests.test_community_access import add_membership, make_user

ADMIN = MembershipRole.COMMUNITY_ADMIN
MEMBER = MembershipRole.MEMBER


@pytest.fixture
def setup():
    communities = InMemoryCommunityRepository()
    memberships = InMemoryMembershipRepository(communities)
    creator = make_user()
    community = communities.add(NewCommunity(name="Los Pinos"), creator.id, is_active=True)
    use_case = ChangeMembershipRole(CommunityAccess(communities, memberships), memberships)
    return use_case, memberships, community, creator


@pytest.fixture
def platform_admin():
    return make_user(PlatformRole.PLATFORM_ADMIN)


def role_of(memberships, community, user) -> MembershipRole:
    return memberships.get(community.id, user.id).role


def test_platform_admin_appoints_and_removes_an_admin(setup, platform_admin) -> None:
    use_case, memberships, community, creator = setup
    member = make_user()
    add_membership(memberships, community, member, MembershipStatus.APPROVED)

    appointed = use_case.execute(platform_admin, community.id, member.id, ADMIN)
    assert appointed.membership.role is ADMIN
    assert appointed.membership.status is MembershipStatus.APPROVED

    removed = use_case.execute(platform_admin, community.id, creator.id, MEMBER)
    assert removed.membership.role is MEMBER
    assert removed.membership.status is MembershipStatus.APPROVED
    assert role_of(memberships, community, member) is ADMIN


def test_last_admin_keeps_the_role(setup, platform_admin) -> None:
    use_case, memberships, community, creator = setup

    with pytest.raises(MembershipChangeRejected) as error:
        use_case.execute(platform_admin, community.id, creator.id, MEMBER)

    assert error.value.detail == "La comunidad debe tener al menos un administrador."
    assert role_of(memberships, community, creator) is ADMIN


@pytest.mark.parametrize(
    "status", [MembershipStatus.PENDING, MembershipStatus.REJECTED, MembershipStatus.BLOCKED]
)
def test_only_approved_members(setup, platform_admin, status) -> None:
    use_case, memberships, community, _ = setup
    user = make_user()
    add_membership(memberships, community, user, status)

    with pytest.raises(MembershipChangeRejected) as error:
        use_case.execute(platform_admin, community.id, user.id, ADMIN)

    assert error.value.detail == "Solo se puede cambiar el rol de un miembro aprobado."
    assert role_of(memberships, community, user) is MEMBER


def test_same_role_is_a_no_op(setup, platform_admin) -> None:
    use_case, memberships, community, creator = setup

    # El único administrador sigue siéndolo: no se comprueba el último administrador.
    detail = use_case.execute(platform_admin, community.id, creator.id, ADMIN)

    assert detail.membership.role is ADMIN


def test_moderator_is_not_assignable(setup, platform_admin) -> None:
    use_case, memberships, community, _ = setup
    member = make_user()
    add_membership(memberships, community, member, MembershipStatus.APPROVED)

    with pytest.raises(MembershipChangeRejected):
        use_case.execute(platform_admin, community.id, member.id, MembershipRole.MODERATOR)


def test_community_admins_and_members_cannot_change_roles(setup) -> None:
    use_case, memberships, community, creator = setup
    member = make_user()
    add_membership(memberships, community, member, MembershipStatus.APPROVED)

    for actor, target in ((creator, member), (member, member)):
        with pytest.raises(PermissionDenied):
            use_case.execute(actor, community.id, target.id, ADMIN)
    assert role_of(memberships, community, member) is MEMBER


def test_unknown_community_or_membership(setup, platform_admin) -> None:
    use_case, _, community, _ = setup

    with pytest.raises(CommunityNotFound):
        use_case.execute(platform_admin, uuid.uuid4(), uuid.uuid4(), ADMIN)
    with pytest.raises(MembershipNotFound):
        use_case.execute(platform_admin, community.id, uuid.uuid4(), ADMIN)
