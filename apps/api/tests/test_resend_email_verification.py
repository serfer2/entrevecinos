import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import EmailVerificationIssuer, hash_token
from entrevecinos.application.users.resend_email_verification import ResendEmailVerification
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from tests.fakes import (
    InMemoryEmailQuotaRepository,
    InMemoryEmailVerificationRepository,
    InMemoryUserRepository,
)

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
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


@pytest.fixture
def resend(
    users: InMemoryUserRepository,
    verifications: InMemoryEmailVerificationRepository,
    issuer: EmailVerificationIssuer,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
) -> ResendEmailVerification:
    quota = EmailQuota(quota_counts, 5000, reset_day=6, clock=clock)
    return ResendEmailVerification(users, verifications, issuer, quota, clock)


def exhaust(quota_counts: InMemoryEmailQuotaRepository, clock: Clock) -> None:
    from entrevecinos.domain.mail.quota import current_period

    quota_counts.counts[current_period(clock(), 6).start] = 5000


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


def test_resend_uses_one_email_of_the_quota(
    resend: ResendEmailVerification, quota_counts: InMemoryEmailQuotaRepository, pending: User
) -> None:
    assert resend.execute(EMAIL) is not None
    assert sum(quota_counts.counts.values()) == 1


def test_resend_that_sends_nothing_does_not_use_the_quota(
    resend: ResendEmailVerification, quota_counts: InMemoryEmailQuotaRepository
) -> None:
    assert resend.execute("nadie@example.com") is None
    assert quota_counts.counts == {}


@pytest.mark.parametrize("email", [EMAIL, "nadie@example.com"])
def test_without_quota_fails_the_same_whether_the_account_exists_or_not(
    resend: ResendEmailVerification,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
    pending: User,
    email: str,
) -> None:
    exhaust(quota_counts, clock)

    with pytest.raises(EmailQuotaExceeded):
        resend.execute(email)
