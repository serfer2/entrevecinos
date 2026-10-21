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
    assert db_session.scalars(select(EmailVerificationModel)).one().used_at is not None
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
ALREADY_VERIFIED = {"detail": "Tu correo ya está validado.", "code": "email_already_verified"}
SUPERSEDED = {
    "detail": "Este enlace ya no es válido porque te hemos enviado uno más reciente.",
    "code": "verification_superseded",
    "email": EMAIL,
}


def test_used_token_returns_400_already_verified(client: TestClient) -> None:
    register_pending(client, EMAIL)
    token = sent_emails(client).last_token(EMAIL)
    assert verify(client, token).status_code == 200

    response = verify(client, token)

    assert response.status_code == 400
    assert response.json() == ALREADY_VERIFIED


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


RESEND_URL = "/v1/auth/email-verification/resend"
RESENT = {"detail": "Si el correo está pendiente de validación, te enviaremos un enlace nuevo."}


def resend(client: TestClient, email: str = EMAIL):
    return client.post(RESEND_URL, json={"email": email})


def age_verifications(db_session: Session, seconds: int = 61) -> None:
    """Hace que los enlaces parezcan creados hace `seconds` segundos (límite de reenvío)."""
    db_session.execute(
        update(EmailVerificationModel).values(
            created_at=EmailVerificationModel.created_at - timedelta(seconds=seconds)
        )
    )


def test_resend_sends_new_link_and_invalidates_previous(
    client: TestClient, db_session: Session
) -> None:
    register_pending(client, EMAIL)
    previous = sent_emails(client).last_token(EMAIL)
    age_verifications(db_session)

    response = resend(client, "Vecino@Example.COM")

    assert response.status_code == 202
    assert response.json() == RESENT
    emails = sent_emails(client).sent
    assert len(emails) == 2
    new = sent_emails(client).last_token(EMAIL)
    assert new != previous
    db_session.expire_all()
    stored = db_session.scalars(
        select(EmailVerificationModel).where(EmailVerificationModel.superseded_at.is_(None))
    ).one()
    expected = datetime.now(UTC) + timedelta(hours=24)
    assert abs(stored.expires_at - expected) < timedelta(minutes=1)
    assert verify(client, previous).json() == SUPERSEDED
    assert verify(client, new).status_code == 200


def test_superseded_token_of_pending_account_returns_400_with_email(
    client: TestClient, db_session: Session
) -> None:
    register_pending(client, EMAIL)
    previous = sent_emails(client).last_token(EMAIL)
    age_verifications(db_session)
    assert resend(client).status_code == 202

    response = verify(client, previous)

    assert response.status_code == 400
    assert response.json() == SUPERSEDED
    assert stored_user(db_session).is_active is False


def test_superseded_token_of_verified_account_returns_400_already_verified(
    client: TestClient, db_session: Session
) -> None:
    register_pending(client, EMAIL)
    previous = sent_emails(client).last_token(EMAIL)
    age_verifications(db_session)
    assert resend(client).status_code == 202
    assert verify(client, sent_emails(client).last_token(EMAIL)).status_code == 200

    response = verify(client, previous)

    assert response.status_code == 400
    assert response.json() == ALREADY_VERIFIED


def test_resend_after_expiry_sends_working_link(client: TestClient, db_session: Session) -> None:
    register_pending(client, EMAIL)
    db_session.execute(
        update(EmailVerificationModel).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    )
    age_verifications(db_session)

    assert resend(client).status_code == 202

    assert verify(client, sent_emails(client).last_token(EMAIL)).status_code == 200


def test_resend_within_60_seconds_sends_nothing(client: TestClient) -> None:
    register_pending(client, EMAIL)

    response = resend(client)

    assert response.status_code == 202
    assert response.json() == RESENT
    assert len(sent_emails(client).sent) == 1


def test_resend_unknown_email_sends_nothing(client: TestClient) -> None:
    response = resend(client, "nadie@example.com")

    assert response.status_code == 202
    assert response.json() == RESENT
    assert sent_emails(client).sent == []


def test_resend_verified_account_sends_nothing(client: TestClient, db_session: Session) -> None:
    register_pending(client, EMAIL)
    assert verify(client, sent_emails(client).last_token(EMAIL)).status_code == 200

    response = resend(client)

    assert response.status_code == 202
    assert response.json() == RESENT
    assert len(sent_emails(client).sent) == 1


@pytest.mark.parametrize("body", [{}, {"email": "mal"}, {"email": EMAIL, "extra": 1}])
def test_resend_invalid_body_returns_422(client: TestClient, body: dict) -> None:
    assert client.post(RESEND_URL, json=body).status_code == 422
