import dataclasses
from datetime import UTC, datetime

import pytest

from entrevecinos.application.users.authenticate_user import AuthenticateUser, LoginCommand
from entrevecinos.application.users.get_current_user import GetCurrentUser
from entrevecinos.domain.users.entities import NewUser
from entrevecinos.domain.users.errors import InvalidCredentials, NotAuthenticated
from tests.fakes import FakePasswordHasher, FakeTokenIssuer, InMemoryUserRepository

PASSWORD = "UnaClaveSegura123!"


@pytest.fixture
def users() -> InMemoryUserRepository:
    repository = InMemoryUserRepository()
    repository.add(NewUser(email="vecino@example.com", full_name="Alex"), f"hashed:{PASSWORD}")
    return repository


@pytest.fixture
def hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def authenticate(users: InMemoryUserRepository, hasher: FakePasswordHasher) -> AuthenticateUser:
    return AuthenticateUser(users, hasher, FakeTokenIssuer())


def set_user(users: InMemoryUserRepository, **changes: object) -> None:
    user = users.get_by_email("vecino@example.com")
    users.users[user.id] = dataclasses.replace(user, **changes)


def test_valid_credentials_issue_token(authenticate: AuthenticateUser) -> None:
    user, token = authenticate.execute(LoginCommand(email=" VECINO@example.com", password=PASSWORD))

    assert user.email == "vecino@example.com"
    assert token.token == f"token-for:{user.id}"


def test_wrong_password_is_rejected(authenticate: AuthenticateUser) -> None:
    with pytest.raises(InvalidCredentials):
        authenticate.execute(LoginCommand(email="vecino@example.com", password="otra-clave-123"))


def test_unknown_email_still_verifies_a_password(
    authenticate: AuthenticateUser, hasher: FakePasswordHasher
) -> None:
    with pytest.raises(InvalidCredentials):
        authenticate.execute(LoginCommand(email="nadie@example.com", password=PASSWORD))

    assert hasher.verified == [None]


@pytest.mark.parametrize(
    "changes", [{"is_active": False}, {"deleted_at": datetime(2026, 1, 1, tzinfo=UTC)}]
)
def test_inactive_or_deleted_users_cannot_log_in(
    authenticate: AuthenticateUser, users: InMemoryUserRepository, changes: dict[str, object]
) -> None:
    set_user(users, **changes)

    with pytest.raises(InvalidCredentials):
        authenticate.execute(LoginCommand(email="vecino@example.com", password=PASSWORD))


def test_outdated_hash_is_replaced(
    authenticate: AuthenticateUser, users: InMemoryUserRepository
) -> None:
    user = users.get_by_email("vecino@example.com")
    users.password_hashes[user.id] = f"old:{PASSWORD}"

    authenticate.execute(LoginCommand(email="vecino@example.com", password=PASSWORD))

    assert users.password_hashes[user.id] == f"hashed:{PASSWORD}"


def test_current_user_rejects_inactive_user(users: InMemoryUserRepository) -> None:
    user = users.get_by_email("vecino@example.com")
    assert GetCurrentUser(users).execute(user.id) == user

    set_user(users, is_active=False)

    with pytest.raises(NotAuthenticated):
        GetCurrentUser(users).execute(user.id)
