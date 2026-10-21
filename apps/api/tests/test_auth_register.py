import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import EmailVerificationModel, UserModel
from tests.api_helpers import register, sent_emails

pytestmark = pytest.mark.db

URL = "/v1/auth/register"
PASSWORD = "UnaClaveSegura123!"


def payload(**overrides: object) -> dict[str, object]:
    return {"email": "vecino@example.com", "password": PASSWORD, "full_name": "Alex Vecino"} | (
        overrides
    )


def user_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(UserModel))


def stored_user(db_session: Session, email: str = "vecino@example.com") -> UserModel:
    return db_session.scalars(select(UserModel).where(UserModel.email == email)).one()


def test_register_creates_inactive_user_without_token(
    client: TestClient, db_session: Session, email_sender
) -> None:
    before = datetime.now(UTC)
    response = client.post(URL, json=payload(phone="+34600111222"))

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"email", "verification_expires_at"}
    assert body["email"] == "vecino@example.com"
    expires_at = datetime.fromisoformat(body["verification_expires_at"])
    assert before + timedelta(hours=24) <= expires_at <= datetime.now(UTC) + timedelta(hours=24)
    assert "password" not in str(body).lower()

    user = stored_user(db_session)
    assert user.full_name == "Alex Vecino"
    assert user.phone == "+34600111222"
    assert user.platform_role == "user"
    assert user.is_active is False
    assert user.email_verified_at is None
    assert user.password_hash.startswith("$argon2id$")


def test_register_sends_verification_email(
    client: TestClient, db_session: Session, email_sender
) -> None:
    client.post(URL, json=payload())

    [email] = email_sender.sent
    assert email.to == "vecino@example.com"
    assert "http://localhost:3000/verificar-correo?token=" in email.text
    token = email_sender.last_token("vecino@example.com")
    stored = db_session.scalars(select(EmailVerificationModel)).one()
    assert stored.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert stored.user_id == stored_user(db_session).id


def test_register_keeps_account_when_email_fails(
    client: TestClient, db_session: Session, email_sender, caplog: pytest.LogCaptureFixture
) -> None:
    def fail(email: object) -> None:
        raise OSError("SMTP caído")

    email_sender.send = fail

    response = client.post(URL, json=payload())

    assert response.status_code == 201
    assert stored_user(db_session).is_active is False
    assert "No se pudo enviar el correo" in caplog.text


def test_register_trims_name_and_normalizes_email(client: TestClient, db_session: Session) -> None:
    response = client.post(URL, json=payload(email="Vecino@Example.COM", full_name="  Alex  "))

    assert response.status_code == 201
    assert response.json()["email"] == "vecino@example.com"
    assert stored_user(db_session).full_name == "Alex"


def test_register_blank_phone_is_stored_as_null(client: TestClient, db_session: Session) -> None:
    client.post(URL, json=payload(phone="  "))

    assert stored_user(db_session).phone is None


@pytest.mark.parametrize("email", ["vecino@example.com", "Vecino@Example.COM"])
def test_register_verified_email_returns_409_in_use(
    client: TestClient, db_session: Session, email: str
) -> None:
    register(client, "vecino@example.com")

    response = client.post(URL, json=payload(email=email, full_name="Otra persona"))

    assert response.status_code == 409
    assert response.json() == {"detail": "El correo ya está en uso.", "code": "email_in_use"}
    assert user_count(db_session) == 1


@pytest.mark.parametrize("email", ["vecino@example.com", "Vecino@Example.COM"])
def test_register_pending_email_returns_409_pending_without_changes(
    client: TestClient, db_session: Session, email: str
) -> None:
    client.post(URL, json=payload())
    emails_before = len(sent_emails(client).sent)

    response = client.post(URL, json=payload(email=email, full_name="Otra persona"))

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Este correo está pendiente de validación.",
        "code": "email_pending_verification",
    }
    assert user_count(db_session) == 1
    assert stored_user(db_session).full_name == "Alex Vecino"
    assert len(sent_emails(client).sent) == emails_before


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
