import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import hash_token
from entrevecinos.application.users.password_reset import PasswordResetIssuer
from entrevecinos.application.users.request_password_reset import RequestPasswordReset
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from tests.fakes import (
    InMemoryEmailQuotaRepository,
    InMemoryPasswordResetRepository,
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
def resets() -> InMemoryPasswordResetRepository:
    return InMemoryPasswordResetRepository()


@pytest.fixture
def clock() -> Clock:
    # El repositorio en memoria fecha los enlaces con la hora real.
    return Clock(datetime.now(UTC))


@pytest.fixture
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


@pytest.fixture
def request_reset(
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
) -> RequestPasswordReset:
    issuer = PasswordResetIssuer(resets, "http://web.test/", timedelta(minutes=60), clock)
    quota = EmailQuota(quota_counts, 5000, reset_day=6, clock=clock)
    return RequestPasswordReset(users, resets, issuer, quota, clock)


@pytest.fixture
def active(users: InMemoryUserRepository) -> User:
    user = users.add(NewUser(email=EMAIL, full_name="Alex <Vecino>"), "hash")
    return users.mark_email_verified(user.id)


def token_of(text: str) -> str:
    return text.split("token=", 1)[1].split()[0]


def test_sends_a_link_that_expires_in_60_minutes(
    request_reset: RequestPasswordReset,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
    active: User,
) -> None:
    message = request_reset.execute("  Vecino@Example.COM ")

    assert message is not None
    assert message.to == EMAIL
    assert message.subject == "Restablece tu contraseña de EntreVecinos"
    assert "http://web.test/restablecer-contrasena/enlace?token=" in message.text
    assert "caduca en 60 minutos" in message.text
    assert "Alex &lt;Vecino&gt;" in message.html
    stored = resets.get(hash_token(token_of(message.text)))
    assert stored is not None
    assert stored.user_id == active.id
    assert stored.expires_at == clock.now + timedelta(minutes=60)


def test_stores_only_the_hash_of_the_token(
    request_reset: RequestPasswordReset, resets: InMemoryPasswordResetRepository, active: User
) -> None:
    message = request_reset.execute(EMAIL)

    assert message is not None
    assert token_of(message.text) not in resets.resets


def test_new_link_replaces_the_previous_one_after_a_minute(
    request_reset: RequestPasswordReset,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
    active: User,
) -> None:
    first = request_reset.execute(EMAIL)
    clock.now += timedelta(seconds=61)

    second = request_reset.execute(EMAIL)

    assert first is not None and second is not None
    assert resets.get(hash_token(token_of(first.text))) is None
    assert resets.get(hash_token(token_of(second.text))) is not None


def test_does_not_send_twice_within_60_seconds(
    request_reset: RequestPasswordReset, clock: Clock, active: User
) -> None:
    assert request_reset.execute(EMAIL) is not None
    clock.now += timedelta(seconds=59)

    assert request_reset.execute(EMAIL) is None


def test_ignores_unknown_email(request_reset: RequestPasswordReset) -> None:
    assert request_reset.execute("nadie@example.com") is None


def test_sends_to_account_pending_verification(
    request_reset: RequestPasswordReset, users: InMemoryUserRepository
) -> None:
    users.add(NewUser(email=EMAIL, full_name="Alex"), "hash")

    assert request_reset.execute(EMAIL) is not None


def test_ignores_deleted_account(
    request_reset: RequestPasswordReset, users: InMemoryUserRepository, active: User
) -> None:
    users.users[active.id] = dataclasses.replace(active, deleted_at=datetime.now(UTC))

    assert request_reset.execute(EMAIL) is None


def test_ignores_deactivated_account_with_verified_email(
    request_reset: RequestPasswordReset, users: InMemoryUserRepository, active: User
) -> None:
    users.users[active.id] = dataclasses.replace(active, is_active=False)

    assert request_reset.execute(EMAIL) is None


def test_sends_to_platform_admin(
    request_reset: RequestPasswordReset, users: InMemoryUserRepository, active: User
) -> None:
    users.users[active.id] = dataclasses.replace(
        active, platform_role=PlatformRole.PLATFORM_ADMIN, email_verified_at=None
    )

    assert request_reset.execute(EMAIL) is not None


def test_each_link_uses_one_email_of_the_quota(
    request_reset: RequestPasswordReset,
    quota_counts: InMemoryEmailQuotaRepository,
    active: User,
) -> None:
    assert request_reset.execute(EMAIL) is not None
    assert sum(quota_counts.counts.values()) == 1


def test_request_that_sends_nothing_does_not_use_the_quota(
    request_reset: RequestPasswordReset, quota_counts: InMemoryEmailQuotaRepository
) -> None:
    assert request_reset.execute("nadie@example.com") is None
    assert quota_counts.counts == {}


@pytest.mark.parametrize("email", [EMAIL, "nadie@example.com"])
def test_without_quota_fails_the_same_whether_the_account_exists_or_not(
    request_reset: RequestPasswordReset,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
    active: User,
    email: str,
) -> None:
    quota_counts.counts[current_period(clock(), 6).start] = 5000

    with pytest.raises(EmailQuotaExceeded):
        request_reset.execute(email)
