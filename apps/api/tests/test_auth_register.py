import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import UserModel
from tests.conftest import TEST_JWT_SECRET

pytestmark = pytest.mark.db

URL = "/v1/auth/register"
PASSWORD = "UnaClaveSegura123!"


def payload(**overrides: object) -> dict[str, object]:
    return {"email": "vecino@example.com", "password": PASSWORD, "full_name": "Alex Vecino"} | (
        overrides
    )


def user_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(UserModel))


def test_register_creates_user_and_returns_token(client: TestClient, db_session: Session) -> None:
    response = client.post(URL, json=payload(phone="+34600111222"))

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 86400
    user = body["user"]
    assert user["email"] == "vecino@example.com"
    assert user["full_name"] == "Alex Vecino"
    assert user["phone"] == "+34600111222"
    assert user["platform_role"] == "user"
    assert user["is_active"] is True
    assert user["avatar_url"] is None
    assert "password" not in str(body).lower()

    claims = jwt.decode(body["access_token"], TEST_JWT_SECRET, algorithms=["HS256"])
    assert claims["sub"] == user["id"]
    assert claims["exp"] - claims["iat"] == 86400

    stored = db_session.get(UserModel, uuid.UUID(user["id"]))
    assert stored.password_hash.startswith("$argon2id$")


def test_register_trims_name_and_normalizes_email(client: TestClient) -> None:
    response = client.post(URL, json=payload(email="Vecino@Example.COM", full_name="  Alex  "))

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "vecino@example.com"
    assert response.json()["user"]["full_name"] == "Alex"


def test_register_blank_phone_is_stored_as_null(client: TestClient) -> None:
    response = client.post(URL, json=payload(phone="  "))

    assert response.json()["user"]["phone"] is None


@pytest.mark.parametrize("email", ["vecino@example.com", "Vecino@Example.COM"])
def test_register_duplicate_email_returns_409(
    client: TestClient, db_session: Session, email: str
) -> None:
    client.post(URL, json=payload())

    response = client.post(URL, json=payload(email=email, full_name="Otra persona"))

    assert response.status_code == 409
    assert response.json() == {"detail": "El correo ya está en uso."}
    assert user_count(db_session) == 1


def test_register_invalid_data_returns_422_per_field(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        URL, json={"email": "no-es-correo", "password": "corta", "full_name": " "}
    )

    assert response.status_code == 422
    locs = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert locs == {("body", "email"), ("body", "password"), ("body", "full_name")}
    assert user_count(db_session) == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "x" * 129},
        {"full_name": "x" * 121},
        {"phone": "1" * 33},
        {"email": f"{'x' * 310}@example.com"},
        {"platform_role": "platform_admin"},
    ],
)
def test_register_rejects_out_of_contract_values(
    client: TestClient, overrides: dict[str, object]
) -> None:
    assert client.post(URL, json=payload(**overrides)).status_code == 422


def test_register_422_does_not_echo_input(client: TestClient) -> None:
    response = client.post(URL, json=payload(password="secreto-1"))

    assert response.status_code == 422
    assert "secreto-1" not in response.text
    assert all(set(error) == {"loc", "msg", "type"} for error in response.json()["detail"])
