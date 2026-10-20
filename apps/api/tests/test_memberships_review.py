import uuid

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


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com", full_name="Ana Admin")


@pytest.fixture
def applicant(client: TestClient) -> dict:
    return register(
        client, "solicitante@example.com", full_name="Sara Solicitante", phone="600111222"
    )


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


def memberships(client: TestClient, account: dict, community_id: str, **params: object):
    return client.get(
        f"/v1/communities/{community_id}/memberships", params=params, headers=account["headers"]
    )


def test_admin_lists_pending_requests_without_contact_data(
    client: TestClient, admin: dict, applicant: dict, community: dict
) -> None:
    request_access(client, applicant, community["id"])

    response = memberships(client, admin, community["id"], status="pending")

    assert response.status_code == 200
    body = response.json()
    assert (body["total"], body["page"], body["page_size"]) == (1, 1, 20)
    [item] = body["items"]
    assert item["user"] == {
        "id": applicant["user"]["id"],
        "full_name": "Sara Solicitante",
        "avatar_url": None,
    }
    assert item["status"] == "pending"
    assert "email" not in str(body) and "600111222" not in str(body)


def test_list_without_filter_orders_oldest_first(
    client: TestClient, admin: dict, applicant: dict, community: dict
) -> None:
    request_access(client, applicant, community["id"])

    items = memberships(client, admin, community["id"]).json()["items"]

    assert [i["user"]["id"] for i in items] == [admin["user"]["id"], applicant["user"]["id"]]


def test_approve(client: TestClient, admin: dict, applicant: dict, community: dict) -> None:
    request_access(client, applicant, community["id"])

    response = review(client, admin, community["id"], applicant["user"]["id"], "approved")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["reviewed_by"] == admin["user"]["id"]
    assert body["reviewed_at"] is not None and body["joined_at"] is not None
    mine = client.get("/v1/users/me/memberships", headers=applicant["headers"]).json()["items"]
    assert mine[0]["status"] == "approved"


def test_reject(client: TestClient, admin: dict, applicant: dict, community: dict) -> None:
    request_access(client, applicant, community["id"])

    response = review(client, admin, community["id"], applicant["user"]["id"], "rejected")

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["joined_at"] is None
    assert memberships(client, admin, community["id"], status="pending").json()["total"] == 0
    again = request_access(client, applicant, community["id"])
    assert (again.status_code, again.json()["status"]) == (409, "rejected")


@pytest.mark.parametrize(("first", "second"), [("rejected", "approved"), ("approved", "rejected")])
def test_cannot_review_twice(
    client: TestClient, admin: dict, applicant: dict, community: dict, first: str, second: str
) -> None:
    request_access(client, applicant, community["id"])
    review(client, admin, community["id"], applicant["user"]["id"], first)

    response = review(client, admin, community["id"], applicant["user"]["id"], second)

    assert response.status_code == 409
    assert response.json() == {"detail": "La solicitud ya se ha revisado."}


def test_unknown_membership_or_community(client: TestClient, admin: dict, community: dict) -> None:
    assert review(client, admin, community["id"], str(uuid.uuid4()), "approved").status_code == 404
    assert memberships(client, admin, str(uuid.uuid4())).status_code == 404


@pytest.mark.parametrize(
    "body", [{"status": "blocked"}, {"status": "pending"}, {"role": "moderator"}, {}]
)
def test_unsupported_changes_are_rejected(
    client: TestClient, admin: dict, applicant: dict, community: dict, body: dict
) -> None:
    request_access(client, applicant, community["id"])

    response = client.patch(
        f"/v1/communities/{community['id']}/memberships/{applicant['user']['id']}",
        json=body,
        headers=admin["headers"],
    )

    assert response.status_code == 422


def test_members_without_role_and_outsiders_are_forbidden(
    client: TestClient, admin: dict, applicant: dict, community: dict
) -> None:
    member = register(client, "miembro@example.com")
    outsider = register(client, "ajeno@example.com")
    join(client, admin, member, community["id"])
    request_access(client, applicant, community["id"])

    for account in (member, outsider, applicant):
        listed = memberships(client, account, community["id"])
        reviewed = review(client, account, community["id"], applicant["user"]["id"], "approved")
        assert (listed.status_code, listed.json()) == (403, FORBIDDEN)
        assert (reviewed.status_code, reviewed.json()) == (403, FORBIDDEN)

    pending = memberships(client, admin, community["id"], status="pending").json()
    assert pending["total"] == 1


def test_platform_admin_can_review_any_community(
    client: TestClient, admin: dict, applicant: dict, community: dict, db_session: Session
) -> None:
    platform_admin = register(client, "plataforma@example.com")
    make_platform_admin(db_session, platform_admin)
    request_access(client, applicant, community["id"])

    assert memberships(client, platform_admin, community["id"]).status_code == 200
    response = review(client, platform_admin, community["id"], applicant["user"]["id"], "approved")
    assert response.status_code == 200


def test_pagination(client: TestClient, admin: dict, community: dict) -> None:
    for number in range(3):
        request_access(client, register(client, f"v{number}@example.com"), community["id"])

    body = memberships(client, admin, community["id"], page=2, page_size=2).json()

    assert (len(body["items"]), body["total"]) == (2, 4)


def test_requires_authentication(client: TestClient, community: dict) -> None:
    assert client.get(f"/v1/communities/{community['id']}/memberships").status_code == 401
