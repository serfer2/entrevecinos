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
