import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.users.email_verification import EmailVerificationIssuer, hash_token
from entrevecinos.application.users.resend_email_verification import ResendEmailVerification
from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from tests.fakes import InMemoryEmailVerificationRepository, InMemoryUserRepository

EMAIL = "vecino@example.com"


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
    # El repositorio en memoria fecha los enlaces con la hora real.
    return Clock(datetime.now(UTC))


@pytest.fixture
def issuer(
    verifications: InMemoryEmailVerificationRepository, clock: Clock
) -> EmailVerificationIssuer:
    return EmailVerificationIssuer(verifications, "http://web.test", timedelta(hours=24), clock)


@pytest.fixture
def resend(
    users: InMemoryUserRepository,
    verifications: InMemoryEmailVerificationRepository,
    issuer: EmailVerificationIssuer,
    clock: Clock,
) -> ResendEmailVerification:
    return ResendEmailVerification(users, verifications, issuer, clock)


@pytest.fixture
def pending(users: InMemoryUserRepository) -> User:
    return users.add(NewUser(email=EMAIL, full_name="Alex Vecino"), "hash")


def token_of(text: str) -> str:
    return text.split("token=", 1)[1].split()[0]


def test_sends_new_link_and_invalidates_previous(
    resend: ResendEmailVerification,
    issuer: EmailVerificationIssuer,
    verifications: InMemoryEmailVerificationRepository,
    clock: Clock,
    pending: User,
) -> None:
    previous, _ = issuer.issue(pending)
    clock.now += timedelta(seconds=61)

    message = resend.execute("  Vecino@Example.COM ")

    assert message is not None
    assert message.to == EMAIL
    new_token = token_of(message.text)
    assert verifications.get(hash_token(token_of(previous.text))).superseded_at is not None
    stored = verifications.get(hash_token(new_token))
    assert stored is not None
    assert stored.superseded_at is None
    assert stored.expires_at == clock.now + timedelta(hours=24)


def test_sends_link_when_none_exists(resend: ResendEmailVerification, pending: User) -> None:
    assert resend.execute(EMAIL) is not None


def test_does_not_resend_within_60_seconds(
    resend: ResendEmailVerification, issuer: EmailVerificationIssuer, clock: Clock, pending: User
) -> None:
    issuer.issue(pending)
    clock.now += timedelta(seconds=59)

    assert resend.execute(EMAIL) is None


def test_ignores_unknown_email(resend: ResendEmailVerification) -> None:
    assert resend.execute("nadie@example.com") is None


def test_ignores_verified_account(
    resend: ResendEmailVerification, users: InMemoryUserRepository, pending: User
) -> None:
    users.mark_email_verified(pending.id)

    assert resend.execute(EMAIL) is None


def test_ignores_platform_admin(
    resend: ResendEmailVerification, users: InMemoryUserRepository, pending: User
) -> None:
    users.users[pending.id] = dataclasses.replace(
        pending, platform_role=PlatformRole.PLATFORM_ADMIN
    )

    assert resend.execute(EMAIL) is None
