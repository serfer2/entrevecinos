from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import EmailVerificationModel, UserModel
from tests.api_helpers import PASSWORD, register_pending, sent_emails
from tests.conftest import TEST_JWT_SECRET

pytestmark = pytest.mark.db

URL = "/v1/auth/email-verification"
EMAIL = "vecino@example.com"


def verify(client: TestClient, token: str):
    return client.post(URL, json={"token": token})


def login(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post("/v1/auth/token", json={"email": email, "password": password})


def stored_user(db_session: Session) -> UserModel:
    db_session.expire_all()
    return db_session.scalars(select(UserModel).where(UserModel.email == EMAIL)).one()


def test_valid_token_activates_account_and_returns_token(
    client: TestClient, db_session: Session
) -> None:
    register_pending(client, EMAIL)

    response = verify(client, sent_emails(client).last_token(EMAIL))

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["user"]["email"] == EMAIL
    assert body["user"]["is_active"] is True
    claims = jwt.decode(body["access_token"], TEST_JWT_SECRET, algorithms=["HS256"])
    assert claims["sub"] == body["user"]["id"]

    user = stored_user(db_session)
    assert user.is_active is True
    assert user.email_verified_at is not None
    assert db_session.scalars(select(EmailVerificationModel)).all() == []
    assert login(client).status_code == 200


def test_expired_token_returns_410_with_email(client: TestClient, db_session: Session) -> None:
    register_pending(client, EMAIL)
    db_session.execute(
        update(EmailVerificationModel).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    )

    response = verify(client, sent_emails(client).last_token(EMAIL))

    assert response.status_code == 410
    assert response.json() == {
        "detail": "El enlace de validación ha caducado.",
        "code": "verification_expired",
        "email": EMAIL,
    }
    assert stored_user(db_session).is_active is False


INVALID = {"detail": "El enlace de validación no es válido.", "code": "verification_invalid"}


def test_used_token_returns_400(client: TestClient) -> None:
    register_pending(client, EMAIL)
    token = sent_emails(client).last_token(EMAIL)
    assert verify(client, token).status_code == 200

    response = verify(client, token)

    assert response.status_code == 400
    assert response.json() == INVALID


def test_unknown_token_returns_400(client: TestClient) -> None:
    response = verify(client, "no-existe")

    assert response.status_code == 400
    assert response.json() == INVALID


@pytest.mark.parametrize("body", [{}, {"token": ""}, {"token": "x", "extra": 1}])
def test_invalid_body_returns_422(client: TestClient, body: dict) -> None:
    assert client.post(URL, json=body).status_code == 422


def test_login_before_verification_returns_403(client: TestClient) -> None:
    register_pending(client, EMAIL)

    response = login(client)

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Tienes que validar tu correo electrónico antes de iniciar sesión.",
        "code": "email_not_verified",
    }


def test_login_before_verification_with_wrong_password_returns_401(client: TestClient) -> None:
    register_pending(client, EMAIL)

    assert login(client, password="otra-clave-123").status_code == 401


def test_unverified_platform_admin_can_log_in(client: TestClient, db_session: Session) -> None:
    register_pending(client, EMAIL)
    db_session.execute(
        update(UserModel)
        .where(UserModel.email == EMAIL)
        .values(platform_role="platform_admin", is_active=True)
    )

    response = login(client)

    assert response.status_code == 200
    assert response.json()["user"]["platform_role"] == "platform_admin"
