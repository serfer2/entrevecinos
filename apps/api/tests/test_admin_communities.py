import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityModel
from tests.api_helpers import (
    create_community,
    create_pending_community,
    make_platform_admin,
    register,
)

pytestmark = pytest.mark.db


@pytest.fixture
def neighbour(client: TestClient) -> dict:
    return register(client, "vecino@example.com")


@pytest.fixture
def platform_admin(client: TestClient, db_session: Session) -> dict:
    account = register(client, "admin@example.com")
    make_platform_admin(db_session, account)
    return account


def set_creation_order(db_session: Session, *communities: dict) -> None:
    """`now()` es el mismo en toda la transacción de la prueba: fija fechas distintas."""
    base = datetime(2026, 1, 1, tzinfo=UTC)
    for days, community in enumerate(communities):
        db_session.get(CommunityModel, uuid.UUID(community["id"])).created_at = base + timedelta(
            days=days
        )
    db_session.flush()


def approve(client: TestClient, account: dict, community_id: object, body: dict | None = None):
    return client.patch(
        f"/v1/admin/communities/{community_id}",
        json={"is_active": True} if body is None else body,
        headers=account["headers"],
    )


def test_lists_pending_communities_oldest_first(
    client: TestClient, neighbour: dict, platform_admin: dict, db_session: Session
) -> None:
    # Cada vecino solo puede tener una comunidad pendiente: hacen falta creadores distintos.
    other = register(client, "otra@example.com")
    second = create_pending_community(client, neighbour, name="Segunda")
    active = create_community(client, platform_admin, name="Activa")
    first = create_pending_community(client, other, name="Primera")
    set_creation_order(db_session, first, active, second)

    response = client.get(
        "/v1/admin/communities", params={"is_active": "false"}, headers=platform_admin["headers"]
    )

    assert response.status_code == 200
    body = response.json()
    assert [c["id"] for c in body["items"]] == [first["id"], second["id"]]
    assert (body["total"], body["page"]) == (2, 1)


def test_lists_all_communities_without_filter(
    client: TestClient, neighbour: dict, platform_admin: dict, db_session: Session
) -> None:
    pending = create_pending_community(client, neighbour, name="Pendiente")
    active = create_community(client, platform_admin, name="Activa")
    set_creation_order(db_session, pending, active)

    response = client.get(
        "/v1/admin/communities", params={"page_size": 1}, headers=platform_admin["headers"]
    )

    assert response.json()["total"] == 2
    assert [c["name"] for c in response.json()["items"]] == ["Pendiente"]


def test_approves_a_pending_community(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_pending_community(client, neighbour)

    response = approve(client, platform_admin, community["id"])

    assert response.status_code == 200
    assert response.json() == {**community, "is_active": True}
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200
    search = client.get("/v1/communities", headers=neighbour["headers"]).json()
    assert [c["id"] for c in search["items"]] == [community["id"]]


def test_approving_an_active_community_changes_nothing(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_community(client, neighbour)

    response = approve(client, platform_admin, community["id"])

    assert response.status_code == 200
    assert response.json() == community


def test_platform_admin_creates_active_communities(
    client: TestClient, platform_admin: dict, neighbour: dict
) -> None:
    response = client.post(
        "/v1/communities", json={"name": "Barrio"}, headers=platform_admin["headers"]
    )

    assert response.status_code == 201
    community = response.json()
    assert community["is_active"] is True
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200
    search = client.get("/v1/communities", headers=neighbour["headers"]).json()
    assert [c["id"] for c in search["items"]] == [community["id"]]
    mine = client.get("/v1/users/me/memberships", headers=platform_admin["headers"]).json()
    assert [(m["community"]["id"], m["role"]) for m in mine["items"]] == [
        (community["id"], "community_admin")
    ]


def test_unknown_community_is_not_found(client: TestClient, platform_admin: dict) -> None:
    assert approve(client, platform_admin, uuid.uuid4()).status_code == 404


@pytest.mark.parametrize("body", [{"is_active": False}, {}, {"is_active": True, "name": "X"}])
def test_only_approval_is_supported(
    client: TestClient, neighbour: dict, platform_admin: dict, body: dict
) -> None:
    community = create_pending_community(client, neighbour)

    assert approve(client, platform_admin, community["id"], body).status_code == 422


def test_only_platform_admins_can_review(client: TestClient, neighbour: dict) -> None:
    community = create_pending_community(client, neighbour)

    listing = client.get("/v1/admin/communities", headers=neighbour["headers"])

    assert listing.status_code == 403
    assert approve(client, neighbour, community["id"]).status_code == 403
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 404


def test_requires_authentication(client: TestClient, neighbour: dict) -> None:
    community = create_pending_community(client, neighbour)

    assert client.get("/v1/admin/communities").status_code == 401
    assert (
        client.patch(
            f"/v1/admin/communities/{community['id']}", json={"is_active": True}
        ).status_code
        == 401
    )


# Rechazo de comunidades pendientes (TK-112, HU-47).

NOT_PENDING = {"detail": "Solo se pueden rechazar comunidades pendientes de aprobación."}


def reject(client: TestClient, account: dict, community_id: object):
    return client.delete(f"/v1/admin/communities/{community_id}", headers=account["headers"])


def test_rejects_a_pending_community(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_pending_community(client, neighbour)

    response = reject(client, platform_admin, community["id"])

    assert response.status_code == 204
    assert response.content == b""
    pending = client.get(
        "/v1/admin/communities", params={"is_active": "false"}, headers=platform_admin["headers"]
    ).json()
    assert pending["items"] == []
    mine = client.get("/v1/users/me/memberships", headers=neighbour["headers"]).json()
    assert mine["items"] == []
    assert approve(client, platform_admin, community["id"]).status_code == 404
    # Ya no tiene una pendiente: puede crear otra comunidad.
    assert create_pending_community(client, neighbour, name="Otra")["is_active"] is False


def test_active_communities_cannot_be_rejected(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_community(client, neighbour)

    response = reject(client, platform_admin, community["id"])

    assert (response.status_code, response.json()) == (409, NOT_PENDING)
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200


def test_rejecting_an_unknown_community(client: TestClient, platform_admin: dict) -> None:
    assert reject(client, platform_admin, uuid.uuid4()).status_code == 404
    assert reject(client, platform_admin, "no-es-un-uuid").status_code == 422


def test_only_platform_admins_reject(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    pending = create_pending_community(client, neighbour)
    active = create_community(client, platform_admin)

    assert reject(client, neighbour, pending["id"]).status_code == 403  # su propio creador
    assert reject(client, platform_admin, active["id"]).status_code == 409
    community_admin = register(client, "gestora@example.com")
    managed = create_community(client, community_admin, name="Gestionada")
    assert reject(client, community_admin, managed["id"]).status_code == 403
    pending_after = client.get(
        "/v1/admin/communities", params={"is_active": "false"}, headers=platform_admin["headers"]
    ).json()
    assert [c["id"] for c in pending_after["items"]] == [pending["id"]]


# Aviso por correo de una comunidad nueva (TK-111, HU-46).

NEW_COMMUNITY_SUBJECT = "Nueva comunidad pendiente: Urbanización Los Olivos"


def new_community_notices(email_sender) -> list:
    return [e for e in email_sender.sent if e.subject == NEW_COMMUNITY_SUBJECT]


def test_platform_admins_are_notified_of_a_new_pending_community(
    client: TestClient, db_session: Session, email_sender, neighbour: dict, platform_admin: dict
) -> None:
    other_admin = register(client, "otra-admin@example.com", full_name="Otra Admin")
    make_platform_admin(db_session, other_admin)

    community = create_pending_community(client, neighbour, city="Majadahonda")

    notices = new_community_notices(email_sender)
    assert sorted(n.to for n in notices) == ["admin@example.com", "otra-admin@example.com"]
    assert "vecino@example.com" in notices[0].text
    assert f"/admin/comunidades#comunidad-{community['id']}" in notices[0].text
    assert "Majadahonda" in notices[0].text


def test_no_notice_when_a_platform_admin_creates_a_community(
    client: TestClient, email_sender, platform_admin: dict
) -> None:
    create_community_response = client.post(
        "/v1/communities",
        json={"name": "Urbanización Los Olivos"},
        headers=platform_admin["headers"],
    )

    assert create_community_response.status_code == 201
    assert new_community_notices(email_sender) == []


def test_community_is_created_without_notice_when_the_quota_is_exhausted(
    client: TestClient, db_session: Session, email_sender, neighbour: dict, platform_admin: dict
) -> None:
    from entrevecinos.domain.mail.quota import current_period
    from entrevecinos.infrastructure.db.models import EmailQuotaModel

    period = current_period(datetime.now(UTC), reset_day=6).start
    db_session.get_one(EmailQuotaModel, period).sent = 5000
    db_session.flush()

    community = create_pending_community(client, neighbour)

    assert community["is_active"] is False
    assert new_community_notices(email_sender) == []


def test_list_platform_admins(
    client: TestClient, db_session: Session, neighbour: dict, platform_admin: dict
) -> None:
    from entrevecinos.infrastructure.db.models import UserModel
    from entrevecinos.infrastructure.users.sqlalchemy_user_repository import (
        SqlAlchemyUserRepository,
    )

    inactive = register(client, "inactiva@example.com", full_name="Inactiva")
    make_platform_admin(db_session, inactive)
    db_session.get(UserModel, uuid.UUID(inactive["user"]["id"])).is_active = False
    db_session.flush()

    admins = SqlAlchemyUserRepository(db_session).list_platform_admins()

    assert [a.email for a in admins] == ["admin@example.com"]
