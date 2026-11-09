"""Aviso por correo de una comunidad nueva a los administradores de plataforma (TK-111)."""

import dataclasses
import uuid
from datetime import UTC, datetime

import pytest

from entrevecinos.application.communities.community_notices import CommunityNotices
from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.domain.communities.entities import Community
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.domain.users.entities import PlatformRole, User
from tests.fakes import InMemoryEmailQuotaRepository, InMemoryUserRepository

NOW = datetime(2026, 11, 9, 10, 0, tzinfo=UTC)
LIMIT = 5000


def account(name: str, email: str, **changes: object) -> User:
    base = User(
        id=uuid.uuid4(),
        email=email,
        full_name=name,
        phone="600000000",
        platform_role=PlatformRole.USER,
        is_active=True,
        created_at=datetime(2026, 3, 2, 9, 0, tzinfo=UTC),
        email_verified_at=NOW,
    )
    return dataclasses.replace(base, **changes)


def community(**changes: object) -> Community:
    base = Community(
        id=uuid.uuid4(),
        name="Los Olivos <norte>",
        description="Urbanización & alrededores",
        postal_code="28220",
        city="Majadahonda",
        created_by=uuid.uuid4(),
        is_active=False,
        created_at=NOW,
    )
    return dataclasses.replace(base, **changes)


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


@pytest.fixture
def notices(users, quota_counts) -> CommunityNotices:
    quota = EmailQuota(quota_counts, LIMIT, reset_day=6, clock=lambda: NOW)
    return CommunityNotices(users, quota, "https://entrevecinos.test/")


def add(users: InMemoryUserRepository, user: User) -> User:
    users.users[user.id] = user
    return user


@pytest.fixture
def creator(users) -> User:
    return add(users, account("Víctor <Vecino>", "victor@example.com", phone="611111111"))


def platform_admin(users, name: str, email: str, **changes: object) -> User:
    return add(users, account(name, email, platform_role=PlatformRole.PLATFORM_ADMIN, **changes))


def test_notifies_each_platform_admin_with_all_the_details(notices, users, creator) -> None:
    platform_admin(users, "Pablo Plataforma", "pablo@example.com")
    platform_admin(users, "Berta Plataforma", "berta@example.com")
    platform_admin(users, "Inactiva", "inactiva@example.com", is_active=False)
    platform_admin(users, "Borrada", "borrada@example.com", deleted_at=NOW)
    pending = community(created_by=creator.id)

    messages = notices.community_created(pending, creator)

    assert [m.to for m in messages] == ["berta@example.com", "pablo@example.com"]
    message = messages[0]
    assert message.subject == "Nueva comunidad pendiente: Los Olivos <norte>"
    link = f"https://entrevecinos.test/admin/comunidades#comunidad-{pending.id}"
    for expected in (
        "Hola, Berta Plataforma:",
        "Víctor <Vecino> ha creado la comunidad Los Olivos <norte> y está pendiente de aprobación.",
        "- Descripción: Urbanización & alrededores",
        "- Ciudad: Majadahonda",
        "- Código postal: 28220",
        "- Creada el: 09/11/2026",
        "- Correo: victor@example.com",
        "- Teléfono: 611111111",
        "- Alta en EntreVecinos: 02/03/2026",
        link,
    ):
        assert expected in message.text
    assert "Los Olivos &lt;norte&gt;" in message.html
    assert "Urbanización &amp; alrededores" in message.html
    assert "<norte>" not in message.html
    assert f'href="{link}"' in message.html


def test_missing_fields_have_placeholders(notices, users, creator) -> None:
    platform_admin(users, "Pablo Plataforma", "pablo@example.com")
    creator = add(users, dataclasses.replace(creator, phone=None))

    [message] = notices.community_created(
        community(description=None, city=None, postal_code=None), creator
    )

    for expected in ("Sin descripción", "- Ciudad: —", "- Código postal: —", "Sin teléfono"):
        assert expected in message.text


def test_active_communities_are_not_notified(notices, users, creator) -> None:
    platform_admin(users, "Pablo Plataforma", "pablo@example.com")

    assert notices.community_created(community(is_active=True), creator) == []


def test_each_notice_uses_the_quota_and_stops_when_exhausted(
    notices, users, creator, quota_counts
) -> None:
    platform_admin(users, "Ana", "ana@example.com")
    platform_admin(users, "Berta", "berta@example.com")
    period = current_period(NOW, reset_day=6).start
    quota_counts.counts[period] = LIMIT - 1

    messages = notices.community_created(community(), creator)

    assert [m.to for m in messages] == ["ana@example.com"]
    assert quota_counts.sent(period) == LIMIT
