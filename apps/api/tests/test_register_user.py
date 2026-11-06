from datetime import UTC, datetime, timedelta

import pytest

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import EmailVerificationIssuer, hash_token
from entrevecinos.application.users.register_user import RegisterUser, RegisterUserCommand
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.users.entities import PlatformRole
from entrevecinos.domain.users.errors import EmailAlreadyRegistered, EmailPendingVerification
from tests.fakes import (
    FakePasswordHasher,
    InMemoryEmailQuotaRepository,
    InMemoryEmailVerificationRepository,
    InMemoryUserRepository,
)

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def verifications() -> InMemoryEmailVerificationRepository:
    return InMemoryEmailVerificationRepository()


@pytest.fixture
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


def make_register_user(
    users: InMemoryUserRepository,
    verifications: InMemoryEmailVerificationRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    limit: int = 5000,
) -> RegisterUser:
    issuer = EmailVerificationIssuer(
        verifications, "http://web.test/", timedelta(hours=24), clock=lambda: NOW
    )
    quota = EmailQuota(quota_counts, limit, reset_day=6, clock=lambda: NOW)
    return RegisterUser(users, FakePasswordHasher(), issuer, quota)


@pytest.fixture
def register_user(
    users: InMemoryUserRepository,
    verifications: InMemoryEmailVerificationRepository,
    quota_counts: InMemoryEmailQuotaRepository,
) -> RegisterUser:
    return make_register_user(users, verifications, quota_counts)


def command(**overrides: str | None) -> RegisterUserCommand:
    values = {
        "email": "vecino@example.com",
        "password": "UnaClaveSegura123!",
        "full_name": "Alex Vecino",
    }
    return RegisterUserCommand(**{**values, **overrides})


def test_registers_inactive_user_pending_verification(
    register_user: RegisterUser, users: InMemoryUserRepository
) -> None:
    user = register_user.execute(command(phone="+34600111222")).user

    assert user.email == "vecino@example.com"
    assert user.full_name == "Alex Vecino"
    assert user.phone == "+34600111222"
    assert user.platform_role is PlatformRole.USER
    assert user.is_active is False
    assert user.email_verification_pending is True
    assert users.password_hashes[user.id] == "hashed:UnaClaveSegura123!"


def test_prepares_verification_email_valid_for_24_hours(
    register_user: RegisterUser, verifications: InMemoryEmailVerificationRepository
) -> None:
    registration = register_user.execute(command())
    email = registration.verification_email

    assert registration.verification_expires_at == NOW + timedelta(hours=24)
    assert email.to == "vecino@example.com"
    assert "Alex Vecino" in email.text
    assert "24 horas" in email.text
    token = email.text.split("http://web.test/verificar-correo?token=", 1)[1].split()[0]
    assert token in email.html
    # Solo se guarda el hash del token.
    assert list(verifications.verifications) == [hash_token(token)]
    stored = verifications.verifications[hash_token(token)]
    assert stored.user_id == registration.user.id
    assert stored.expires_at == NOW + timedelta(hours=24)


def test_escapes_name_in_html(register_user: RegisterUser) -> None:
    email = register_user.execute(command(full_name="<b>Alex</b>")).verification_email

    assert "<b>Alex</b>" not in email.html
    assert "&lt;b&gt;Alex&lt;/b&gt;" in email.html


def test_normalizes_email(register_user: RegisterUser) -> None:
    user = register_user.execute(command(email="  Vecino@Example.COM ")).user

    assert user.email == "vecino@example.com"


def test_rejects_registered_email_ignoring_case(
    register_user: RegisterUser, users: InMemoryUserRepository
) -> None:
    users.mark_email_verified(register_user.execute(command()).user.id)

    with pytest.raises(EmailAlreadyRegistered):
        register_user.execute(command(email="VECINO@example.com"))


def test_rejects_email_pending_verification_without_changes(
    register_user: RegisterUser, users: InMemoryUserRepository
) -> None:
    first = register_user.execute(command()).user

    with pytest.raises(EmailPendingVerification):
        register_user.execute(command(email="VECINO@example.com", full_name="Otra persona"))

    assert list(users.users.values()) == [first]


def test_registration_uses_one_email_of_the_quota(
    register_user: RegisterUser, quota_counts: InMemoryEmailQuotaRepository
) -> None:
    register_user.execute(command())

    assert sum(quota_counts.counts.values()) == 1


def test_without_quota_no_account_is_created(
    users: InMemoryUserRepository,
    verifications: InMemoryEmailVerificationRepository,
    quota_counts: InMemoryEmailQuotaRepository,
) -> None:
    register_user = make_register_user(users, verifications, quota_counts, limit=1)
    register_user.execute(command())

    with pytest.raises(EmailQuotaExceeded):
        register_user.execute(command(email="otra@example.com"))

    assert users.get_by_email("otra@example.com") is None


def test_duplicate_email_does_not_use_the_quota(
    register_user: RegisterUser, quota_counts: InMemoryEmailQuotaRepository
) -> None:
    register_user.execute(command())

    with pytest.raises(EmailPendingVerification):
        register_user.execute(command())

    assert sum(quota_counts.counts.values()) == 1
