"""Cambio de rol de un miembro por el `platform_admin` (TK-109, HU-45)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.api_helpers import (
    create_community,
    join,
    make_platform_admin,
    register,
    request_access,
    review,
)

pytestmark = pytest.mark.db

FORBIDDEN = {"detail": "No tienes permisos para realizar esta acción."}
LAST_ADMIN = {"detail": "La comunidad debe tener al menos un administrador."}
ONLY_APPROVED = {"detail": "Solo se puede cambiar el rol de un miembro aprobado."}


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com", full_name="Ana Admin")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def member(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "miembro@example.com", full_name="Mario Miembro")
    join(client, admin, account, community["id"])
    return account


@pytest.fixture
def platform_admin(client: TestClient, db_session: Session) -> dict:
    account = register(client, "plataforma@example.com", full_name="Pablo Plataforma")
    make_platform_admin(db_session, account)
    return account


def change_role(client: TestClient, actor: dict, community_id: str, user_id: str, role: str):
    return client.patch(
        f"/v1/communities/{community_id}/memberships/{user_id}",
        json={"role": role},
        headers=actor["headers"],
    )


def list_members(client: TestClient, account: dict, community_id: str):
    return client.get(f"/v1/communities/{community_id}/memberships", headers=account["headers"])


def test_platform_admin_appoints_an_admin(
    client: TestClient, platform_admin: dict, member: dict, community: dict
) -> None:
    assert list_members(client, member, community["id"]).status_code == 403

    response = change_role(
        client, platform_admin, community["id"], member["user"]["id"], "community_admin"
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert (body["role"], body["status"]) == ("community_admin", "approved")
    assert body["joined_at"] is not None
    assert list_members(client, member, community["id"]).status_code == 200


def test_new_admin_is_notified_of_requests(
    client: TestClient, platform_admin: dict, member: dict, community: dict, email_sender
) -> None:
    change_role(client, platform_admin, community["id"], member["user"]["id"], "community_admin")
    applicant = register(client, "solicitante@example.com")
    email_sender.sent.clear()

    assert request_access(client, applicant, community["id"]).status_code == 201

    assert sorted(e.to for e in email_sender.sent) == ["admin@example.com", "miembro@example.com"]


def test_platform_admin_removes_the_role(
    client: TestClient, platform_admin: dict, admin: dict, member: dict, community: dict
) -> None:
    change_role(client, platform_admin, community["id"], member["user"]["id"], "community_admin")

    response = change_role(client, platform_admin, community["id"], admin["user"]["id"], "member")

    assert response.status_code == 200, response.text
    assert (response.json()["role"], response.json()["status"]) == ("member", "approved")
    assert list_members(client, admin, community["id"]).status_code == 403
    # Ya no es administrador: se le puede bloquear.
    assert (
        review(client, member, community["id"], admin["user"]["id"], "blocked").status_code == 200
    )


def test_last_admin_keeps_the_role(
    client: TestClient, platform_admin: dict, admin: dict, community: dict
) -> None:
    response = change_role(client, platform_admin, community["id"], admin["user"]["id"], "member")

    assert (response.status_code, response.json()) == (409, LAST_ADMIN)
    assert list_members(client, admin, community["id"]).status_code == 200


def test_same_role_is_a_no_op(
    client: TestClient, platform_admin: dict, admin: dict, community: dict
) -> None:
    response = change_role(
        client, platform_admin, community["id"], admin["user"]["id"], "community_admin"
    )

    assert (response.status_code, response.json()["role"]) == (200, "community_admin")


@pytest.mark.parametrize("status", ["pending", "rejected", "blocked"])
def test_only_approved_members(
    client: TestClient,
    platform_admin: dict,
    admin: dict,
    member: dict,
    community: dict,
    status: str,
) -> None:
    target = member
    if status == "blocked":
        review(client, admin, community["id"], member["user"]["id"], "blocked")
    else:
        target = register(client, "solicitante@example.com")
        request_access(client, target, community["id"])
        if status == "rejected":
            review(client, admin, community["id"], target["user"]["id"], "rejected")

    response = change_role(
        client, platform_admin, community["id"], target["user"]["id"], "community_admin"
    )

    assert (response.status_code, response.json()) == (409, ONLY_APPROVED)


def test_community_admins_cannot_change_roles(
    client: TestClient, admin: dict, member: dict, community: dict
) -> None:
    appoint = change_role(client, admin, community["id"], member["user"]["id"], "community_admin")
    demote_self = change_role(client, admin, community["id"], admin["user"]["id"], "member")
    by_member = change_role(
        client, member, community["id"], member["user"]["id"], "community_admin"
    )

    for response in (appoint, demote_self, by_member):
        assert (response.status_code, response.json()) == (403, FORBIDDEN)


def test_unknown_membership_is_not_found(
    client: TestClient, platform_admin: dict, community: dict
) -> None:
    outsider = register(client, "ajeno@example.com")

    response = change_role(
        client, platform_admin, community["id"], outsider["user"]["id"], "community_admin"
    )

    assert response.status_code == 404
