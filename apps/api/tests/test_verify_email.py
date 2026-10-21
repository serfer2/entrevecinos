from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.users.email_verification import EmailVerificationIssuer
from entrevecinos.application.users.verify_email import VerifyEmail
from entrevecinos.domain.users.entities import NewUser, User
from entrevecinos.domain.users.errors import VerificationExpired, VerificationInvalid
from tests.fakes import FakeTokenIssuer, InMemoryEmailVerificationRepository, InMemoryUserRepository

ISSUED = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)


class Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def verifications() -> InMemoryEmailVerificationRepository:
    return InMemoryEmailVerificationRepository()


@pytest.fixture
def clock() -> Clock:
    return Clock(ISSUED)


@pytest.fixture
def user(users: InMemoryUserRepository) -> User:
    return users.add(NewUser(email="vecino@example.com", full_name="Alex"), "h")


def issue(verifications: InMemoryEmailVerificationRepository, clock: Clock, user: User) -> str:
    issuer = EmailVerificationIssuer(verifications, "http://web.test", timedelta(hours=24), clock)
    email, _ = issuer.issue(user)
    return email.text.split("token=", 1)[1].split()[0]


@pytest.fixture
def verify(
    users: InMemoryUserRepository, verifications: InMemoryEmailVerificationRepository, clock: Clock
) -> VerifyEmail:
    return VerifyEmail(users, verifications, FakeTokenIssuer(), clock)


def test_valid_token_activates_account_and_issues_token(
    verify: VerifyEmail, verifications, clock: Clock, user: User
) -> None:
    token = issue(verifications, clock, user)
    clock.now = ISSUED + timedelta(hours=23, minutes=59)

    verified, access = verify.execute(token)

    assert verified.is_active is True
    assert verified.email_verified_at is not None
    assert verified.email_verification_pending is False
    assert access.token == f"token-for:{user.id}"
    assert verifications.verifications == {}


def test_expired_token_is_rejected_with_email(
    verify: VerifyEmail, users: InMemoryUserRepository, verifications, clock: Clock, user: User
) -> None:
    token = issue(verifications, clock, user)
    clock.now = ISSUED + timedelta(hours=24)

    with pytest.raises(VerificationExpired) as error:
        verify.execute(token)

    assert error.value.email == "vecino@example.com"
    assert users.get_by_id(user.id).is_active is False


def test_used_token_is_invalid(
    verify: VerifyEmail, verifications, clock: Clock, user: User
) -> None:
    token = issue(verifications, clock, user)
    verify.execute(token)

    with pytest.raises(VerificationInvalid):
        verify.execute(token)


def test_replaced_token_is_invalid(
    verify: VerifyEmail, verifications, clock: Clock, user: User
) -> None:
    old = issue(verifications, clock, user)
    new = issue(verifications, clock, user)

    with pytest.raises(VerificationInvalid):
        verify.execute(old)
    assert verify.execute(new)[0].is_active is True


def test_unknown_token_is_invalid(verify: VerifyEmail) -> None:
    with pytest.raises(VerificationInvalid):
        verify.execute("no-existe")
