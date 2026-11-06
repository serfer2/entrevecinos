from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from entrevecinos.domain.mail.quota import current_period
from entrevecinos.infrastructure.db.models import EmailQuotaModel, UserModel

pytestmark = pytest.mark.db

PASSWORD = "UnaClaveSegura123!"


def exhaust_quota(db_session: Session) -> None:
    period = current_period(datetime.now(UTC), reset_day=6).start
    db_session.add(EmailQuotaModel(period_start=period, sent=5000))
    db_session.flush()


def assert_quota_exceeded(response) -> None:
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Ahora mismo no podemos enviar correos. Inténtalo de nuevo más tarde.",
        "code": "email_quota_exceeded",
    }
    assert int(response.headers["Retry-After"]) > 0


def test_register_counts_one_email(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/v1/auth/register",
        json={"email": "vecino@example.com", "password": PASSWORD, "full_name": "Alex Vecino"},
    )

    assert response.status_code == 201
    assert db_session.scalars(select(EmailQuotaModel.sent)).one() == 1


def test_register_without_quota_returns_503_and_creates_nothing(
    client: TestClient, db_session: Session, email_sender
) -> None:
    exhaust_quota(db_session)

    response = client.post(
        "/v1/auth/register",
        json={"email": "vecino@example.com", "password": PASSWORD, "full_name": "Alex Vecino"},
    )

    assert_quota_exceeded(response)
    assert db_session.scalars(select(UserModel)).first() is None
    assert email_sender.sent == []


def test_resend_without_quota_returns_503_even_for_unknown_email(
    client: TestClient, db_session: Session, email_sender
) -> None:
    exhaust_quota(db_session)

    response = client.post(
        "/v1/auth/email-verification/resend", json={"email": "nadie@example.com"}
    )

    assert_quota_exceeded(response)
    assert email_sender.sent == []
