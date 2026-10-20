"""Ayudas para las pruebas de integración de la API."""

from fastapi.testclient import TestClient

PASSWORD = "UnaClaveSegura123!"


def register(
    client: TestClient, email: str, full_name: str = "Alex Vecino", phone: str | None = None
) -> dict:
    """Registra una cuenta y devuelve el `AuthResponse` con `headers` listos para usar."""
    response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": full_name, "phone": phone},
    )
    assert response.status_code == 201, response.text
    account = response.json()
    account["headers"] = {"Authorization": f"Bearer {account['access_token']}"}
    return account


def create_community(client: TestClient, owner: dict, **fields: object) -> dict:
    body = {"name": "Urbanización Los Olivos", **fields}
    response = client.post("/v1/communities", json=body, headers=owner["headers"])
    assert response.status_code == 201, response.text
    return response.json()


def request_access(client: TestClient, account: dict, community_id: str):
    return client.post(f"/v1/communities/{community_id}/memberships", headers=account["headers"])


def review(client: TestClient, admin: dict, community_id: str, user_id: str, status: str):
    return client.patch(
        f"/v1/communities/{community_id}/memberships/{user_id}",
        json={"status": status},
        headers=admin["headers"],
    )


def join(client: TestClient, admin: dict, member: dict, community_id: str) -> None:
    """Solicita el acceso de `member` y lo aprueba con `admin`."""
    assert request_access(client, member, community_id).status_code == 201
    response = review(client, admin, community_id, member["user"]["id"], "approved")
    assert response.status_code == 200, response.text


def make_platform_admin(db_session, account: dict) -> None:
    import uuid

    from entrevecinos.infrastructure.db.models import UserModel

    db_session.get(UserModel, uuid.UUID(account["user"]["id"])).platform_role = "platform_admin"
    db_session.flush()
