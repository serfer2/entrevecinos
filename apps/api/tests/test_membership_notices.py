import dataclasses
import uuid
from datetime import UTC, datetime

import pytest

from entrevecinos.application.communities.membership_notices import MembershipNotices
from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.domain.communities.entities import (
    Community,
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.domain.users.entities import PlatformRole, User
from tests.fakes import (
    InMemoryCommunityRepository,
    InMemoryEmailQuotaRepository,
    InMemoryMembershipRepository,
)

NOW = datetime(2026, 11, 9, 10, 0, tzinfo=UTC)


def user(name: str, email: str, **changes: object) -> User:
    base = User(
        id=uuid.uuid4(),
        email=email,
        full_name=name,
        phone="600000000",
        platform_role=PlatformRole.USER,
        is_active=True,
        created_at=NOW,
        email_verified_at=NOW,
    )
    return dataclasses.replace(base, **changes)


@pytest.fixture
def communities() -> InMemoryCommunityRepository:
    return InMemoryCommunityRepository()


@pytest.fixture
def memberships(communities: InMemoryCommunityRepository) -> InMemoryMembershipRepository:
    return InMemoryMembershipRepository(communities)


@pytest.fixture
def quota_counts() -> InMemoryEmailQuotaRepository:
    return InMemoryEmailQuotaRepository()


@pytest.fixture
def notices(
    memberships: InMemoryMembershipRepository, quota_counts: InMemoryEmailQuotaRepository
) -> MembershipNotices:
    quota = EmailQuota(quota_counts, 5000, reset_day=6, clock=lambda: NOW)
    return MembershipNotices(memberships, quota, "https://entrevecinos.test/")


@pytest.fixture
def ana(memberships: InMemoryMembershipRepository) -> User:
    account = user("Ana Admin", "ana@example.com")
    memberships.users[account.id] = account
    return account


@pytest.fixture
def community(communities: InMemoryCommunityRepository, ana: User) -> Community:
    return communities.add(NewCommunity(name="Los Olivos <norte>"), ana.id, is_active=True)


@pytest.fixture
def requester(memberships: InMemoryMembershipRepository) -> User:
    account = user("Víctor <Vecino>", "victor@example.com", phone="611111111")
    memberships.users[account.id] = account
    return account


def add_member(
    memberships: InMemoryMembershipRepository,
    community: Community,
    account: User,
    role: MembershipRole,
    status: MembershipStatus = MembershipStatus.APPROVED,
) -> None:
    memberships.users[account.id] = account
    memberships.add_request(community.id, account.id)
    key = (community.id, account.id)
    memberships.memberships[key] = dataclasses.replace(
        memberships.memberships[key], role=role, status=status
    )


def test_notifies_the_admin_without_the_requester_contact_details(
    notices: MembershipNotices, community: Community, requester: User
) -> None:
    [message] = notices.request_received(community, requester)

    assert message.to == "ana@example.com"
    assert message.subject == "Nueva solicitud para unirse a Los Olivos <norte>"
    assert "Víctor <Vecino> ha pedido unirse a Los Olivos <norte>." in message.text
    link = f"https://entrevecinos.test/comunidades/{community.id}/gestion/solicitudes"
    assert link in message.text
    assert "Víctor &lt;Vecino&gt;" in message.html
    for contact in ("victor@example.com", "611111111"):
        assert contact not in message.text
        assert contact not in message.html


def test_one_message_per_approved_admin_only(
    notices: MembershipNotices,
    memberships: InMemoryMembershipRepository,
    community: Community,
    requester: User,
) -> None:
    add_member(
        memberships,
        community,
        user("Berta Admin", "berta@example.com"),
        MembershipRole.COMMUNITY_ADMIN,
    )
    add_member(
        memberships,
        community,
        user("Mario Moderador", "mario@example.com"),
        MembershipRole.MODERATOR,
    )
    add_member(
        memberships, community, user("Mía Miembro", "mia@example.com"), MembershipRole.MEMBER
    )
    add_member(
        memberships,
        community,
        user("Pablo Pendiente", "pablo@example.com"),
        MembershipRole.COMMUNITY_ADMIN,
        MembershipStatus.PENDING,
    )
    add_member(
        memberships,
        community,
        user("Iván Inactivo", "ivan@example.com", is_active=False),
        MembershipRole.COMMUNITY_ADMIN,
    )

    messages = notices.request_received(community, requester)

    assert [m.to for m in messages] == ["ana@example.com", "berta@example.com"]


def test_each_message_uses_one_email_of_the_quota(
    notices: MembershipNotices,
    memberships: InMemoryMembershipRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    community: Community,
    requester: User,
) -> None:
    add_member(
        memberships,
        community,
        user("Berta Admin", "berta@example.com"),
        MembershipRole.COMMUNITY_ADMIN,
    )

    assert len(notices.request_received(community, requester)) == 2
    assert sum(quota_counts.counts.values()) == 2


def test_without_quota_prepares_no_more_messages(
    notices: MembershipNotices,
    memberships: InMemoryMembershipRepository,
    quota_counts: InMemoryEmailQuotaRepository,
    community: Community,
    requester: User,
) -> None:
    add_member(
        memberships,
        community,
        user("Berta Admin", "berta@example.com"),
        MembershipRole.COMMUNITY_ADMIN,
    )
    quota_counts.counts[current_period(NOW, 6).start] = 4999

    messages = notices.request_received(community, requester)

    assert [m.to for m in messages] == ["ana@example.com"]
