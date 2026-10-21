"""Ayudas para las pruebas de integración de la API."""

from fastapi.testclient import TestClient

PASSWORD = "UnaClaveSegura123!"


def sent_emails(client: TestClient):
    """`FakeEmailSender` de la app de la prueba."""
    from entrevecinos.presentation.dependencies import get_email_sender

    return client.app.dependency_overrides[get_email_sender]()


def register_pending(
    client: TestClient, email: str, full_name: str = "Alex Vecino", phone: str | None = None
) -> dict:
    """Registra una cuenta sin validar su correo y devuelve la `RegistrationResponse`."""
    response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": full_name, "phone": phone},
    )
    assert response.status_code == 201, response.text
    return response.json()


def verify_email(client: TestClient, email: str):
    token = sent_emails(client).last_token(email.strip().lower())
    return client.post("/v1/auth/email-verification", json={"token": token})


def register(
    client: TestClient, email: str, full_name: str = "Alex Vecino", phone: str | None = None
) -> dict:
    """Registra una cuenta, valida su correo y devuelve el `AuthResponse` con `headers`."""
    register_pending(client, email, full_name, phone)
    response = verify_email(client, email)
    assert response.status_code == 200, response.text
    account = response.json()
    account["headers"] = {"Authorization": f"Bearer {account['access_token']}"}
    return account


def create_pending_community(client: TestClient, owner: dict, **fields: object) -> dict:
    body = {"name": "Urbanización Los Olivos", **fields}
    response = client.post("/v1/communities", json=body, headers=owner["headers"])
    assert response.status_code == 201, response.text
    return response.json()


def approve_community(client: TestClient, community_id: str) -> dict:
    """Aprueba la comunidad directamente en la sesión de la prueba (sin pasar por la API)."""
    import uuid

    from entrevecinos.infrastructure.db.models import CommunityModel
    from entrevecinos.infrastructure.db.session import get_session

    session = client.app.dependency_overrides[get_session]()
    community = session.get(CommunityModel, uuid.UUID(community_id))
    community.is_active = True
    session.flush()
    return community_json(client, community_id)


def community_json(client: TestClient, community_id: str) -> dict:
    import uuid

    from entrevecinos.infrastructure.communities.sqlalchemy_community_repository import (
        community_to_domain,
    )
    from entrevecinos.infrastructure.db.models import CommunityModel
    from entrevecinos.infrastructure.db.session import get_session
    from entrevecinos.presentation.v1.schemas.communities import CommunityResponse

    session = client.app.dependency_overrides[get_session]()
    model = session.get(CommunityModel, uuid.UUID(community_id))
    return CommunityResponse.from_domain(community_to_domain(model)).model_dump(mode="json")


def create_community(client: TestClient, owner: dict, **fields: object) -> dict:
    """Crea una comunidad y la aprueba: la mayoría de pruebas necesitan una comunidad activa."""
    community = create_pending_community(client, owner, **fields)
    return approve_community(client, community["id"])


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


def category_id(client: TestClient, account: dict, slug: str = "otros") -> str:
    response = client.get("/v1/categories", headers=account["headers"])
    return next(c["id"] for c in response.json()["items"] if c["slug"] == slug)


def upload_image(client: TestClient, account: dict) -> str:
    from tests.images import JPEG

    response = client.post(
        "/v1/media", files={"file": ("foto.jpg", JPEG, "image/jpeg")}, headers=account["headers"]
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def listing_body(client: TestClient, account: dict, **fields: object) -> dict:
    return {
        "category_id": category_id(client, account),
        "title": "Bicicleta infantil",
        "description": "Poco uso",
        "type": "sell",
        **fields,
    }


def publish(client: TestClient, account: dict, community_id: str, **fields: object):
    return client.post(
        f"/v1/communities/{community_id}/listings",
        json=listing_body(client, account, **fields),
        headers=account["headers"],
    )


def publish_ok(client: TestClient, account: dict, community_id: str, **fields: object) -> dict:
    response = publish(client, account, community_id, **fields)
    assert response.status_code == 201, response.text
    return response.json()
