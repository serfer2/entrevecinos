import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import hash_token
from entrevecinos.application.users.reset_password import ResetPassword
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.domain.users.entities import NewUser, User
from entrevecinos.domain.users.errors import PasswordResetExpired, PasswordResetInvalid
from tests.fakes import (
    FakePasswordHasher,
    InMemoryEmailQuotaRepository,
    InMemoryPasswordResetRepository,
    InMemoryUserRepository,
)

EMAIL = "vecino@example.com"
TOKEN = "token-del-correo"
NEW_PASSWORD = "OtraClaveSegura456!"


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
    # 10:30 UTC del 8 de noviembre: 11:30 en Madrid (horario de invierno).
    return Clock(datetime(2026, 11, 8, 10, 30, tzinfo=UTC))


@pytest.fixture
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


@pytest.fixture
def reset(
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
) -> ResetPassword:
    quota = EmailQuota(quota_counts, 5000, reset_day=6, clock=clock)
    return ResetPassword(users, resets, FakePasswordHasher(), quota, clock)


@pytest.fixture
def active(users: InMemoryUserRepository) -> User:
    user = users.add(NewUser(email=EMAIL, full_name="Alex <Vecino>"), "hashed:antigua")
    return users.mark_email_verified(user.id)


def issue(resets: InMemoryPasswordResetRepository, user: User, expires_at: datetime) -> None:
    resets.replace(user.id, hash_token(TOKEN), expires_at)


def test_changes_the_password_and_voids_the_links(
    reset: ResetPassword,
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
    active: User,
) -> None:
    issue(resets, active, clock.now + timedelta(minutes=30))

    notice = reset.execute(TOKEN, NEW_PASSWORD)

    assert users.password_hashes[active.id] == f"hashed:{NEW_PASSWORD}"
    assert users.get_by_id(active.id).password_changed_at is not None
    assert resets.resets == {}
    assert notice is not None
    assert notice.to == EMAIL
    assert notice.subject == "Tu contraseña de EntreVecinos ha cambiado"
    assert "se cambió el 08/11/2026 a las 11:30 (hora de Madrid)" in notice.text
    assert "Alex &lt;Vecino&gt;" in notice.html


def test_link_cannot_be_used_twice(
    reset: ResetPassword, resets: InMemoryPasswordResetRepository, clock: Clock, active: User
) -> None:
    issue(resets, active, clock.now + timedelta(minutes=30))
    reset.execute(TOKEN, NEW_PASSWORD)

    with pytest.raises(PasswordResetInvalid):
        reset.execute(TOKEN, "TerceraClave789!")


def test_unknown_link_is_invalid(reset: ResetPassword) -> None:
    with pytest.raises(PasswordResetInvalid):
        reset.execute("inventado", NEW_PASSWORD)


def test_expired_link_does_not_change_the_password(
    reset: ResetPassword,
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
    active: User,
) -> None:
    issue(resets, active, clock.now)

    with pytest.raises(PasswordResetExpired):
        reset.execute(TOKEN, NEW_PASSWORD)

    assert users.password_hashes[active.id] == "hashed:antigua"


@pytest.mark.parametrize(
    "changes", [{"deleted_at": datetime(2026, 11, 8, tzinfo=UTC)}, {"is_active": False}]
)
def test_account_that_can_no_longer_reset_is_invalid(
    reset: ResetPassword,
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
    active: User,
    changes: dict,
) -> None:
    issue(resets, active, clock.now + timedelta(minutes=30))
    users.users[active.id] = dataclasses.replace(active, **changes)

    with pytest.raises(PasswordResetInvalid):
        reset.execute(TOKEN, NEW_PASSWORD)

    assert users.password_hashes[active.id] == "hashed:antigua"


def test_account_pending_verification_becomes_verified(
    reset: ResetPassword,
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    clock: Clock,
) -> None:
    pending = users.add(NewUser(email=EMAIL, full_name="Alex"), "hashed:antigua")
    issue(resets, pending, clock.now + timedelta(minutes=30))

    reset.execute(TOKEN, NEW_PASSWORD)

    user = users.get_by_id(pending.id)
    assert user.is_active
    assert user.email_verified_at is not None


def test_notice_uses_one_email_of_the_quota(
    reset: ResetPassword,
    resets: InMemoryPasswordResetRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
    active: User,
) -> None:
    issue(resets, active, clock.now + timedelta(minutes=30))

    reset.execute(TOKEN, NEW_PASSWORD)

    assert sum(quota_counts.counts.values()) == 1


def test_without_quota_changes_the_password_without_notice(
    reset: ResetPassword,
    users: InMemoryUserRepository,
    resets: InMemoryPasswordResetRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    clock: Clock,
    active: User,
) -> None:
    issue(resets, active, clock.now + timedelta(minutes=30))
    quota_counts.counts[current_period(clock(), 6).start] = 5000

    assert reset.execute(TOKEN, NEW_PASSWORD) is None
    assert users.password_hashes[active.id] == f"hashed:{NEW_PASSWORD}"
