import pytest

from entrevecinos.application.users.update_profile import ProfileChanges, UpdateProfile
from entrevecinos.domain.users.entities import NewUser, User
from tests.fakes import InMemoryUserRepository


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def user(users: InMemoryUserRepository) -> User:
    return users.add(NewUser(email="v@example.com", full_name="Alex", phone="600111222"), "h")


def test_only_name(users: InMemoryUserRepository, user: User) -> None:
    updated = UpdateProfile(users).execute(user.id, ProfileChanges(full_name="Alex García"))

    assert (updated.full_name, updated.phone) == ("Alex García", "600111222")


def test_only_phone(users: InMemoryUserRepository, user: User) -> None:
    updated = UpdateProfile(users).execute(user.id, ProfileChanges(phone="+34 600 000 000"))

    assert (updated.full_name, updated.phone) == ("Alex", "+34 600 000 000")


def test_none_clears_phone(users: InMemoryUserRepository, user: User) -> None:
    updated = UpdateProfile(users).execute(user.id, ProfileChanges(phone=None))

    assert (updated.full_name, updated.phone) == ("Alex", None)


def test_unset_fields_are_not_sent() -> None:
    assert ProfileChanges().as_values() == {}
    assert ProfileChanges(phone=None).as_values() == {"phone": None}
