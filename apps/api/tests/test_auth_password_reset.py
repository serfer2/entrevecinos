from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from entrevecinos.application.users.email_verification import hash_token
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.infrastructure.db.models import EmailQuotaModel, PasswordResetModel, UserModel
from tests.api_helpers import register, register_pending

pytestmark = pytest.mark.db

EMAIL = "vecino@example.com"
REQUESTED = {
    "detail": (
        "Si hay una cuenta con ese correo, te enviaremos un enlace para restablecer la contraseña."
    )
}


def request_reset(client: TestClient, email: str = EMAIL):
    return client.post("/v1/auth/password-reset", json={"email": email})


def reset_emails(email_sender) -> list:
    return [e for e in email_sender.sent if e.subject == "Restablece tu contraseña de EntreVecinos"]


def test_sends_the_link_to_an_active_account(
    client: TestClient, db_session: Session, email_sender
) -> None:
    register(client, EMAIL)

    response = request_reset(client, "Vecino@Example.com")

    assert response.status_code == 202
    assert response.json() == REQUESTED
    [message] = reset_emails(email_sender)
    assert message.to == EMAIL
    assert "/restablecer-contrasena/enlace?token=" in message.text
    token = email_sender.last_token(EMAIL)
    stored = db_session.get(PasswordResetModel, hash_token(token))
    assert stored is not None
    assert db_session.get(PasswordResetModel, token) is None


def test_unknown_email_gets_the_same_answer_and_no_email(client: TestClient, email_sender) -> None:
    response = request_reset(client, "nadie@example.com")

    assert response.status_code == 202
    assert response.json() == REQUESTED
    assert email_sender.sent == []


def test_account_pending_verification_gets_the_link(client: TestClient, email_sender) -> None:
    register_pending(client, EMAIL)

    assert request_reset(client).status_code == 202
    assert len(reset_emails(email_sender)) == 1


def test_deactivated_verified_account_gets_nothing(
    client: TestClient, db_session: Session, email_sender
) -> None:
    register(client, EMAIL)
    user = db_session.scalars(select(UserModel).where(UserModel.email == EMAIL)).one()
    user.is_active = False
    db_session.flush()

    assert request_reset(client).status_code == 202
    assert reset_emails(email_sender) == []


def test_second_request_within_a_minute_sends_nothing(client: TestClient, email_sender) -> None:
    register(client, EMAIL)

    assert request_reset(client).status_code == 202
    assert request_reset(client).status_code == 202

    assert len(reset_emails(email_sender)) == 1


def test_link_uses_one_email_of_the_quota(client: TestClient, db_session: Session) -> None:
    register(client, EMAIL)
    before = db_session.scalars(select(EmailQuotaModel.sent)).one()

    request_reset(client)

    db_session.expire_all()
    assert db_session.scalars(select(EmailQuotaModel.sent)).one() == before + 1


@pytest.mark.parametrize("email", [EMAIL, "nadie@example.com"])
def test_without_quota_returns_503_whether_the_account_exists_or_not(
    client: TestClient, db_session: Session, email_sender, email: str
) -> None:
    register(client, EMAIL)
    sent_before = len(email_sender.sent)
    period = current_period(datetime.now(UTC), reset_day=6).start
    db_session.get_one(EmailQuotaModel, period).sent = 5000
    db_session.flush()

    response = request_reset(client, email)

    assert response.status_code == 503
    assert response.json()["code"] == "email_quota_exceeded"
    assert int(response.headers["Retry-After"]) > 0
    assert len(email_sender.sent) == sent_before


@pytest.mark.parametrize("body", [{}, {"email": "no-es-un-correo"}, {"email": EMAIL, "extra": "x"}])
def test_invalid_body_returns_422(client: TestClient, body: dict) -> None:
    assert client.post("/v1/auth/password-reset", json=body).status_code == 422
