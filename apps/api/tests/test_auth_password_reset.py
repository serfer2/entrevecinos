from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from entrevecinos.application.users.email_verification import hash_token
from entrevecinos.domain.mail.quota import current_period
from entrevecinos.infrastructure.db.models import EmailQuotaModel, PasswordResetModel, UserModel
from tests.api_helpers import PASSWORD, register, register_pending
from tests.conftest import TEST_JWT_SECRET

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


NEW_PASSWORD = "OtraClaveSegura456!"


def reset_token(client: TestClient, email_sender, email: str = EMAIL) -> str:
    assert request_reset(client, email).status_code == 202
    return email_sender.last_token(email)


def confirm(client: TestClient, token: str, password: str = NEW_PASSWORD):
    return client.post(
        "/v1/auth/password-reset/confirm", json={"token": token, "password": password}
    )


def login(client: TestClient, password: str, email: str = EMAIL):
    return client.post("/v1/auth/token", json={"email": email, "password": password})


def test_confirm_changes_the_password_and_sends_a_notice(
    client: TestClient, db_session: Session, email_sender
) -> None:
    register(client, EMAIL)
    token = reset_token(client, email_sender)

    response = confirm(client, token)

    assert response.status_code == 204
    assert response.content == b""
    assert login(client, NEW_PASSWORD).status_code == 200
    assert login(client, PASSWORD).status_code == 401
    assert db_session.scalars(select(PasswordResetModel)).all() == []
    assert email_sender.sent[-1].subject == "Tu contraseña de EntreVecinos ha cambiado"
    assert email_sender.sent[-1].to == EMAIL


def test_confirm_twice_with_the_same_link_is_invalid(client: TestClient, email_sender) -> None:
    register(client, EMAIL)
    token = reset_token(client, email_sender)
    confirm(client, token)

    response = confirm(client, token, "TerceraClave789!")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "El enlace para restablecer la contraseña no es válido.",
        "code": "password_reset_invalid",
    }
    assert login(client, NEW_PASSWORD).status_code == 200


def test_confirm_with_an_expired_link_returns_410(
    client: TestClient, db_session: Session, email_sender
) -> None:
    register(client, EMAIL)
    token = reset_token(client, email_sender)
    db_session.get_one(PasswordResetModel, hash_token(token)).expires_at = datetime(
        2020, 1, 1, tzinfo=UTC
    )
    db_session.flush()

    response = confirm(client, token)

    assert response.status_code == 410
    assert response.json() == {
        "detail": "El enlace para restablecer la contraseña ha caducado.",
        "code": "password_reset_expired",
    }
    assert login(client, PASSWORD).status_code == 200


def test_short_password_returns_422_and_keeps_the_link(client: TestClient, email_sender) -> None:
    register(client, EMAIL)
    token = reset_token(client, email_sender)

    assert confirm(client, token, "corta").status_code == 422
    assert confirm(client, token).status_code == 204


def test_confirm_closes_previous_sessions(client: TestClient, email_sender) -> None:
    account = register(client, EMAIL)
    # Sesión abierta antes del cambio: `iat` en un segundo anterior.
    old = jwt.encode(
        {
            "sub": account["user"]["id"],
            "iat": datetime.now(UTC) - timedelta(seconds=30),
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
    assert me(client, old).status_code == 200

    confirm(client, reset_token(client, email_sender))

    assert me(client, old).status_code == 401
    new = login(client, NEW_PASSWORD).json()["access_token"]
    assert me(client, new).status_code == 200


def test_confirm_verifies_a_pending_account(client: TestClient, email_sender) -> None:
    register_pending(client, EMAIL)

    assert confirm(client, reset_token(client, email_sender)).status_code == 204
    assert login(client, NEW_PASSWORD).status_code == 200


def test_confirm_without_quota_changes_the_password_without_notice(
    client: TestClient, db_session: Session, email_sender
) -> None:
    register(client, EMAIL)
    token = reset_token(client, email_sender)
    sent_before = len(email_sender.sent)
    period = current_period(datetime.now(UTC), reset_day=6).start
    db_session.get_one(EmailQuotaModel, period).sent = 5000
    db_session.flush()

    assert confirm(client, token).status_code == 204
    assert login(client, NEW_PASSWORD).status_code == 200
    assert len(email_sender.sent) == sent_before


def me(client: TestClient, token: str):
    return client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})
