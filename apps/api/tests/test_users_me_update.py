import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import UserModel

pytestmark = pytest.mark.db

PASSWORD = "UnaClaveSegura123!"


def register(client: TestClient, email: str, phone: str | None = "600111222") -> dict:
    response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Alex Vecino", "phone": phone},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def account(client: TestClient) -> dict:
    return register(client, "vecino@example.com")


def patch(client: TestClient, account: dict, body: object):
    return client.patch(
        "/v1/users/me", json=body, headers={"Authorization": f"Bearer {account['access_token']}"}
    )


def stored(db_session: Session, account: dict) -> UserModel:
    db_session.expire_all()
    return db_session.get(UserModel, uuid.UUID(account["user"]["id"]))


def test_updates_name_and_phone(client: TestClient, account: dict, db_session: Session) -> None:
    created_at = stored(db_session, account).created_at
    updated_before = stored(db_session, account).updated_at

    response = patch(
        client, account, {"full_name": "Alex Vecino García", "phone": "+34 600 111 222"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Alex Vecino García"
    assert response.json()["phone"] == "+34 600 111 222"
    me = client.get(
        "/v1/users/me", headers={"Authorization": f"Bearer {account['access_token']}"}
    ).json()
    assert me == response.json()
    row = stored(db_session, account)
    assert row.updated_at > updated_before
    assert row.created_at == created_at


def test_partial_updates(client: TestClient, account: dict) -> None:
    first = patch(client, account, {"full_name": "Nuevo nombre"}).json()
    assert (first["full_name"], first["phone"]) == ("Nuevo nombre", "600111222")

    second = patch(client, account, {"phone": None}).json()
    assert (second["full_name"], second["phone"]) == ("Nuevo nombre", None)


def test_blank_phone_clears_it(client: TestClient, account: dict) -> None:
    assert patch(client, account, {"phone": "  "}).json()["phone"] is None


@pytest.mark.parametrize("full_name", ["", "   ", None])
def test_name_is_required(
    client: TestClient, account: dict, db_session: Session, full_name: str | None
) -> None:
    response = patch(client, account, {"full_name": full_name, "phone": "699999999"})

    assert response.status_code == 422
    assert ["body", "full_name"] in [error["loc"] for error in response.json()["detail"]]
    row = stored(db_session, account)
    assert (row.full_name, row.phone) == ("Alex Vecino", "600111222")


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"phone": "llámame"},
        {"phone": "12345"},
        {"phone": "1" * 33},
        {"full_name": "x" * 121},
        {"email": "otro@example.com"},
        {"platform_role": "platform_admin"},
        {"password": "OtraClaveSegura123!", "current_password": PASSWORD},
        {"avatar_asset_id": None},
    ],
)
def test_rejects_invalid_or_unsupported_fields(
    client: TestClient, account: dict, db_session: Session, body: dict
) -> None:
    assert patch(client, account, body).status_code == 422
    row = stored(db_session, account)
    assert (row.email, row.platform_role, row.full_name) == (
        "vecino@example.com",
        "user",
        "Alex Vecino",
    )


def test_only_own_profile_changes(client: TestClient, account: dict, db_session: Session) -> None:
    other = register(client, "otra@example.com")

    patch(client, account, {"full_name": "Cambiado"})

    assert stored(db_session, other).full_name == "Alex Vecino"


def test_requires_authentication(client: TestClient) -> None:
    response = client.patch("/v1/users/me", json={"full_name": "X"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
