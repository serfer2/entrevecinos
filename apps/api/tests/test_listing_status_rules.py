"""Matriz de transiciones de `ChangeListingStatus` (autor, moderación y moderador-autor)."""

import dataclasses
import uuid

import pytest

from entrevecinos.application.listings.change_status import ChangeListingStatus
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import ListingStatus as S
from entrevecinos.domain.listings.errors import ListingLocked, ListingStatusConflict
from tests.test_community_access import make_user
from tests.test_delete_listing import make_listing


class Access:
    def __init__(self, manager: bool, member: bool = True) -> None:
        self.manager, self.member = manager, member

    def has_role(self, user, community_id, roles):
        return self.manager

    def require_member(self, user, community_id):
        if not self.member:
            raise PermissionDenied


class Listings:
    def __init__(self, listing) -> None:
        self.listing = listing
        self.changes: list = []

    def get(self, listing_id):
        return self.listing

    def set_status(self, listing_id, status, moderator_id):
        self.changes.append((status, moderator_id))
        self.listing = dataclasses.replace(self.listing, status=status)
        return self.listing


def run(current: S, status: S, *, owner: bool, manager: bool, member: bool = True):
    user = make_user()
    listing = dataclasses.replace(make_listing(user.id if owner else uuid.uuid4()), status=current)
    listings = Listings(listing)
    result = ChangeListingStatus(Access(manager, member), listings).execute(
        user, listing.id, status
    )
    return result, listings.changes, user


@pytest.mark.parametrize(
    ("current", "status"),
    [
        (S.ACTIVE, S.RESERVED),
        (S.RESERVED, S.ACTIVE),
        (S.ACTIVE, S.COMPLETED),
        (S.RESERVED, S.COMPLETED),
    ],
)
def test_author_transitions(current: S, status: S) -> None:
    result, changes, _ = run(current, status, owner=True, manager=False)

    assert result.status is status
    assert changes == [(status, None)]


@pytest.mark.parametrize(
    ("current", "status"),
    [(S.ACTIVE, S.HIDDEN), (S.RESERVED, S.HIDDEN), (S.COMPLETED, S.HIDDEN), (S.HIDDEN, S.ACTIVE)],
)
def test_moderation_transitions(current: S, status: S) -> None:
    result, changes, user = run(current, status, owner=False, manager=True)

    assert result.status is status
    assert changes == [(status, user.id if status is S.HIDDEN else None)]


@pytest.mark.parametrize(
    ("current", "status", "detail"),
    [
        (S.ACTIVE, S.ACTIVE, ListingStatusConflict.SAME),
        (S.RESERVED, S.RESERVED, ListingStatusConflict.SAME),
        (S.COMPLETED, S.ACTIVE, ListingStatusConflict.COMPLETED_FINAL),
        (S.COMPLETED, S.RESERVED, ListingStatusConflict.COMPLETED_FINAL),
        (S.COMPLETED, S.COMPLETED, ListingStatusConflict.SAME),
    ],
)
def test_author_conflicts(current: S, status: S, detail: str) -> None:
    with pytest.raises(ListingStatusConflict) as error:
        run(current, status, owner=True, manager=False)
    assert error.value.detail == detail


def test_author_cannot_retire_or_touch_a_retired_listing() -> None:
    with pytest.raises(PermissionDenied):
        run(S.ACTIVE, S.HIDDEN, owner=True, manager=False)
    with pytest.raises(ListingLocked):
        run(S.HIDDEN, S.ACTIVE, owner=True, manager=False)


def test_blocked_author_is_denied() -> None:
    with pytest.raises(PermissionDenied):
        run(S.ACTIVE, S.RESERVED, owner=True, manager=False, member=False)


@pytest.mark.parametrize("status", [S.RESERVED, S.COMPLETED])
def test_moderators_cannot_reserve_or_complete_others(status: S) -> None:
    with pytest.raises(PermissionDenied):
        run(S.ACTIVE, status, owner=False, manager=True)


def test_moderator_author_gets_both_rules() -> None:
    reserved, *_ = run(S.ACTIVE, S.RESERVED, owner=True, manager=True)
    hidden, *_ = run(S.RESERVED, S.HIDDEN, owner=True, manager=True)
    restored, *_ = run(S.HIDDEN, S.ACTIVE, owner=True, manager=True)

    assert (reserved.status, hidden.status, restored.status) == (S.RESERVED, S.HIDDEN, S.ACTIVE)


def test_other_members_are_denied() -> None:
    with pytest.raises(PermissionDenied):
        run(S.ACTIVE, S.RESERVED, owner=False, manager=False)
