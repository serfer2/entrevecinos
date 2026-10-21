import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import UserModel
from entrevecinos.infrastructure.security.jwt_tokens import JwtTokenService
from tests.api_helpers import register
from tests.conftest import TEST_JWT_SECRET

pytestmark = pytest.mark.db

PASSWORD = "UnaClaveSegura123!"
LOGIN_ERROR = {"detail": "Correo o contraseña incorrectos."}
AUTH_ERROR = {"detail": "Autenticación requerida."}


@pytest.fixture
def registered(client: TestClient) -> dict[str, object]:
    return register(client, "vecino@example.com")


def login(client: TestClient, email: str, password: str = PASSWORD):
    return client.post("/v1/auth/token", json={"email": email, "password": password})


def me(client: TestClient, authorization: str | None):
    headers = {"Authorization": authorization} if authorization else {}
    return client.get("/v1/users/me", headers=headers)


def deactivate(db_session: Session, **values: object) -> None:
    db_session.execute(update(UserModel).values(**values))
    db_session.expire_all()


def test_login_returns_token_usable_on_me(client: TestClient, registered: dict) -> None:
    response = login(client, "VECINO@Example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["user"]["id"] == registered["user"]["id"]

    profile = me(client, f"Bearer {body['access_token']}")
    assert profile.status_code == 200
    assert profile.json() == registered["user"]


def test_login_errors_are_indistinguishable(
    client: TestClient, db_session: Session, registered: dict
) -> None:
    responses = [login(client, "nadie@example.com"), login(client, "vecino@example.com", "x" * 12)]
    deactivate(db_session, is_active=False)
    responses.append(login(client, "vecino@example.com"))
    deactivate(db_session, is_active=True, deleted_at=datetime.now(UTC))
    responses.append(login(client, "vecino@example.com"))

    assert {r.status_code for r in responses} == {401}
    assert all(r.json() == LOGIN_ERROR for r in responses)


def test_login_validates_body(client: TestClient) -> None:
    response = client.post("/v1/auth/token", json={"email": "mal", "password": "x", "extra": 1})

    assert response.status_code == 422
    assert all(set(error) == {"loc", "msg", "type"} for error in response.json()["detail"])


def test_outdated_hash_is_rehashed_on_login(
    client: TestClient, db_session: Session, registered: dict
) -> None:
    from pwdlib.hashers.argon2 import Argon2Hasher

    old_hash = Argon2Hasher(time_cost=1, memory_cost=8192).hash(PASSWORD)
    deactivate(db_session, password_hash=old_hash)

    assert login(client, "vecino@example.com").status_code == 200
    stored = db_session.get(UserModel, uuid.UUID(registered["user"]["id"]))
    assert stored.password_hash != old_hash
    assert stored.password_hash.startswith("$argon2id$")


def forged(secret: str = TEST_JWT_SECRET, algorithm: str = "HS256", **claims: object) -> str:
    now = datetime.now(UTC)
    payload = {"sub": str(uuid.uuid4()), "iat": now, "exp": now + timedelta(hours=1)} | claims
    return jwt.encode(payload, secret, algorithm=algorithm)


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Basic dmVjaW5vOmNsYXZl",
        "Bearer no-es-un-jwt",
        "Bearer " + forged(secret="otro-secreto-de-al-menos-32-caracteres!!"),
        "Bearer " + forged(algorithm="none", secret=""),
        "Bearer " + forged(sub="no-es-un-uuid"),
        "Bearer " + forged(),  # firma válida, pero el usuario no existe
    ],
    ids=[
        "sin-cabecera",
        "basic",
        "mal-formado",
        "otra-firma",
        "alg-none",
        "sub-invalido",
        "sin-user",
    ],
)
def test_me_rejects_invalid_tokens(client: TestClient, authorization: str | None) -> None:
    response = me(client, authorization)

    assert response.status_code == 401
    assert response.json() == AUTH_ERROR
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_expired_token(client: TestClient, registered: dict) -> None:
    expired = JwtTokenService(TEST_JWT_SECRET, ttl_seconds=-10).issue(
        uuid.UUID(registered["user"]["id"])
    )

    assert me(client, f"Bearer {expired.token}").status_code == 401


def test_me_rejects_user_deleted_after_token_issued(
    client: TestClient, db_session: Session, registered: dict
) -> None:
    deactivate(db_session, deleted_at=datetime.now(UTC))

    response = me(client, f"Bearer {registered['access_token']}")

    assert response.status_code == 401
    assert response.json() == AUTH_ERROR


def test_openapi_declares_bearer_auth(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert "bearerAuth" in schema["components"]["securitySchemes"]
    assert schema["paths"]["/v1/users/me"]["get"]["security"] == [{"bearerAuth": []}]
    assert "security" not in schema["paths"]["/v1/auth/token"]["post"]
