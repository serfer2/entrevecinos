import pytest

from entrevecinos.application.users.register_user import RegisterUser, RegisterUserCommand
from entrevecinos.domain.users.entities import PlatformRole
from entrevecinos.domain.users.errors import EmailAlreadyRegistered
from tests.fakes import FakePasswordHasher, FakeTokenIssuer, InMemoryUserRepository


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def register_user(users: InMemoryUserRepository) -> RegisterUser:
    return RegisterUser(users, FakePasswordHasher(), FakeTokenIssuer())


def command(**overrides: str | None) -> RegisterUserCommand:
    values = {
        "email": "vecino@example.com",
        "password": "UnaClaveSegura123!",
        "full_name": "Alex Vecino",
    }
    return RegisterUserCommand(**{**values, **overrides})


def test_registers_user_and_issues_token(
    register_user: RegisterUser, users: InMemoryUserRepository
) -> None:
    user, token = register_user.execute(command(phone="+34600111222"))

    assert user.email == "vecino@example.com"
    assert user.full_name == "Alex Vecino"
    assert user.phone == "+34600111222"
    assert user.platform_role is PlatformRole.USER
    assert token.token == f"token-for:{user.id}"
    assert users.password_hashes[user.id] == "hashed:UnaClaveSegura123!"


def test_normalizes_email(register_user: RegisterUser) -> None:
    user, _ = register_user.execute(command(email="  Vecino@Example.COM "))

    assert user.email == "vecino@example.com"


def test_rejects_registered_email_ignoring_case(register_user: RegisterUser) -> None:
    register_user.execute(command())

    with pytest.raises(EmailAlreadyRegistered):
        register_user.execute(command(email="VECINO@example.com"))
