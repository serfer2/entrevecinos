import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityMembershipModel
from tests.api_helpers import (
    create_community,
    join,
    make_platform_admin,
    publish_ok,
    register,
    request_access,
    review,
)

pytestmark = pytest.mark.db


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
def neighbour(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "vecina@example.com", full_name="Vera Vecina")
    join(client, admin, account, community["id"])
    return account


def remove(client: TestClient, actor: dict, community_id: str, user_id: str):
    return client.delete(
        f"/v1/communities/{community_id}/memberships/{user_id}", headers=actor["headers"]
    )


def listing_titles(client: TestClient, account: dict, community_id: str, **params) -> list[str]:
    response = client.get(
        f"/v1/communities/{community_id}/listings", params=params, headers=account["headers"]
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == len(body["items"])
    return [item["title"] for item in body["items"]]


def make_admin(db_session: Session, community: dict, account: dict) -> None:
    db_session.execute(
        update(CommunityMembershipModel)
        .where(
            CommunityMembershipModel.community_id == uuid.UUID(community["id"]),
            CommunityMembershipModel.user_id == uuid.UUID(account["user"]["id"]),
        )
        .values(role="community_admin")
    )


def test_block_and_unblock(client: TestClient, admin: dict, member: dict, community: dict) -> None:
    joined_at = review(client, admin, community["id"], member["user"]["id"], "approved")
    assert joined_at.status_code == 409  # ya aprobado: no se puede volver a aprobar

    blocked = review(client, admin, community["id"], member["user"]["id"], "blocked")
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"

    listing = client.get(f"/v1/communities/{community['id']}/listings", headers=member["headers"])
    assert (listing.status_code, listing.json()["status"]) == (403, "blocked")
    publish = client.post(
        f"/v1/communities/{community['id']}/listings", json={}, headers=member["headers"]
    )
    assert publish.status_code in (403, 422)
    again = request_access(client, member, community["id"])
    assert (again.status_code, again.json()["status"]) == (409, "blocked")

    unblocked = review(client, admin, community["id"], member["user"]["id"], "approved")
    assert unblocked.status_code == 200
    assert unblocked.json()["joined_at"] == blocked.json()["joined_at"]
    assert listing_titles(client, member, community["id"]) == []


def test_cannot_block_admins_or_oneself(
    client: TestClient, admin: dict, member: dict, community: dict, db_session: Session
) -> None:
    other_admin = register(client, "otro-admin@example.com")
    join(client, admin, other_admin, community["id"])
    make_admin(db_session, community, other_admin)

    self_block = review(client, admin, community["id"], admin["user"]["id"], "blocked")
    admin_block = review(client, admin, community["id"], other_admin["user"]["id"], "blocked")

    assert self_block.status_code == 409
    assert admin_block.json() == {
        "detail": "No se puede bloquear a un administrador de la comunidad."
    }


def test_invalid_transitions(client: TestClient, admin: dict, community: dict) -> None:
    pending = register(client, "pendiente@example.com")
    request_access(client, pending, community["id"])

    response = review(client, admin, community["id"], pending["user"]["id"], "blocked")

    assert response.status_code == 409
    assert response.json() == {"detail": "Cambio de estado no permitido."}


def test_blocked_member_listings_are_hidden(
    client: TestClient,
    admin: dict,
    member: dict,
    neighbour: dict,
    community: dict,
) -> None:
    listing = publish_ok(client, member, community["id"], title="Bicicleta del bloqueado")
    reserved = publish_ok(client, member, community["id"], title="Mesa del bloqueado")
    publish_ok(client, neighbour, community["id"], title="Lámpara de Vera")
    client.patch(
        f"/v1/listings/{reserved['id']}",
        json={"title": "Mesa del bloqueado"},
        headers=member["headers"],
    )

    review(client, admin, community["id"], member["user"]["id"], "blocked")

    assert listing_titles(client, neighbour, community["id"]) == ["Lámpara de Vera"]
    assert listing_titles(client, neighbour, community["id"], q="bloqueado") == []
    hidden = client.get(f"/v1/listings/{listing['id']}", headers=neighbour["headers"])
    assert hidden.status_code == 404
    as_admin = client.get(f"/v1/listings/{listing['id']}", headers=admin["headers"])
    assert as_admin.status_code == 200

    review(client, admin, community["id"], member["user"]["id"], "approved")

    assert sorted(listing_titles(client, neighbour, community["id"])) == [
        "Bicicleta del bloqueado",
        "Lámpara de Vera",
        "Mesa del bloqueado",
    ]


def test_expel_hides_listings_and_allows_new_request(
    client: TestClient, admin: dict, member: dict, neighbour: dict, community: dict
) -> None:
    publish_ok(client, member, community["id"], title="Anuncio del expulsado")

    response = remove(client, admin, community["id"], member["user"]["id"])

    assert response.status_code == 204
    assert (
        client.get(
            f"/v1/communities/{community['id']}/listings", headers=member["headers"]
        ).status_code
        == 403
    )
    assert listing_titles(client, neighbour, community["id"]) == []
    assert request_access(client, member, community["id"]).status_code == 201


def test_platform_admin_listings_are_shown_without_approved_membership(
    client: TestClient, db_session: Session, neighbour: dict, community: dict
) -> None:
    platform_admin = register(client, "plataforma@example.com", full_name="Pilar Plataforma")
    make_platform_admin(db_session, platform_admin)
    assert request_access(client, platform_admin, community["id"]).status_code == 201
    listing = publish_ok(client, platform_admin, community["id"], title="Anuncio de la plataforma")

    assert listing_titles(client, neighbour, community["id"]) == ["Anuncio de la plataforma"]
    detail = client.get(f"/v1/listings/{listing['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200


def test_member_can_leave_but_not_remove_others(
    client: TestClient, member: dict, neighbour: dict, community: dict
) -> None:
    assert remove(client, member, community["id"], neighbour["user"]["id"]).status_code == 403
    assert remove(client, member, community["id"], member["user"]["id"]).status_code == 204
    assert remove(client, member, community["id"], member["user"]["id"]).status_code == 404


def test_last_admin_is_protected(
    client: TestClient, admin: dict, community: dict, db_session: Session
) -> None:
    platform_admin = register(client, "plataforma@example.com")
    make_platform_admin(db_session, platform_admin)

    own = remove(client, admin, community["id"], admin["user"]["id"])
    by_platform = remove(client, platform_admin, community["id"], admin["user"]["id"])

    assert own.json() == {"detail": "La comunidad debe tener al menos un administrador."}
    assert (own.status_code, by_platform.status_code) == (409, 409)


def test_admin_cannot_expel_another_admin(
    client: TestClient, admin: dict, community: dict, db_session: Session
) -> None:
    other_admin = register(client, "otro-admin@example.com")
    join(client, admin, other_admin, community["id"])
    make_admin(db_session, community, other_admin)

    assert remove(client, other_admin, community["id"], admin["user"]["id"]).status_code == 403
    assert remove(client, other_admin, community["id"], other_admin["user"]["id"]).status_code == (
        204
    )


def test_list_shows_all_states_ordered(
    client: TestClient, admin: dict, member: dict, neighbour: dict, community: dict
) -> None:
    pending = register(client, "pendiente@example.com", full_name="Pedro Pendiente")
    request_access(client, pending, community["id"])
    review(client, admin, community["id"], member["user"]["id"], "blocked")

    items = client.get(
        f"/v1/communities/{community['id']}/memberships", headers=admin["headers"]
    ).json()["items"]

    assert [(i["user"]["full_name"], i["status"], i["role"]) for i in items] == [
        ("Pedro Pendiente", "pending", "member"),
        ("Ana Admin", "approved", "community_admin"),
        ("Vera Vecina", "approved", "member"),
        ("Mario Miembro", "blocked", "member"),
    ]


def test_unknown_membership_and_authentication(
    client: TestClient, admin: dict, community: dict
) -> None:
    assert remove(client, admin, community["id"], str(uuid.uuid4())).status_code == 404
    assert remove(client, admin, str(uuid.uuid4()), admin["user"]["id"]).status_code == 404
    response = client.delete(f"/v1/communities/{community['id']}/memberships/{uuid.uuid4()}")
    assert response.status_code == 401
