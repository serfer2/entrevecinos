import dataclasses
import uuid

import pytest

from entrevecinos.application.listings.visibility import ListingVisibility
from entrevecinos.domain.communities.entities import MembershipStatus
from entrevecinos.domain.communities.errors import MembershipNotApproved
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import ListingStatus
from entrevecinos.domain.listings.errors import ListingNotFound
from tests.test_community_access import make_user
from tests.test_delete_listing import make_listing


class Access:
    """Membresías y roles simulados: `members` aprobados, `managers` con rol de gestión."""

    def __init__(self, members=(), managers=(), pending=()) -> None:
        self.members, self.managers, self.pending = set(members), set(managers), set(pending)

    def require_member(self, user, community_id):
        if user.id in self.pending:
            raise MembershipNotApproved(MembershipStatus.PENDING)
        if user.id not in self.members | self.managers:
            raise PermissionDenied

    def has_role(self, user, community_id, roles):
        return user.id in self.managers


@pytest.fixture
def people():
    return {name: make_user() for name in ("author", "member", "manager", "pending", "outsider")}


def visibility(people) -> ListingVisibility:
    return ListingVisibility(
        Access(
            members={people["author"].id, people["member"].id},
            managers={people["manager"].id},
            pending={people["pending"].id},
        )
    )


@pytest.mark.parametrize(
    "status", [ListingStatus.ACTIVE, ListingStatus.RESERVED, ListingStatus.COMPLETED]
)
def test_visible_statuses_for_members(people, status) -> None:
    listing = dataclasses.replace(make_listing(people["author"].id), status=status)

    for name in ("author", "member", "manager"):
        visibility(people).require_visible(people[name], listing)


@pytest.mark.parametrize("status", [ListingStatus.HIDDEN, ListingStatus.DRAFT])
def test_restricted_statuses(people, status) -> None:
    listing = dataclasses.replace(make_listing(people["author"].id), status=status)
    rule = visibility(people)

    rule.require_visible(people["author"], listing)
    rule.require_visible(people["manager"], listing)
    with pytest.raises(ListingNotFound):
        rule.require_visible(people["member"], listing)
    assert rule.can_view(people["member"], listing) is False


def test_membership_is_checked_first(people) -> None:
    hidden = dataclasses.replace(make_listing(people["author"].id), status=ListingStatus.HIDDEN)
    rule = visibility(people)

    with pytest.raises(MembershipNotApproved):
        rule.require_visible(people["pending"], hidden)
    with pytest.raises(PermissionDenied):
        rule.require_visible(people["outsider"], hidden)
    assert rule.can_view(people["outsider"], make_listing(uuid.uuid4())) is False
