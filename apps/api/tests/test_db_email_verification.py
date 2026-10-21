from datetime import UTC, datetime, timedelta

import pytest
from alembic import command
from sqlalchemy import Engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import EmailVerificationModel, UserModel
from entrevecinos.infrastructure.users.sqlalchemy_email_verification_repository import (
    SqlAlchemyEmailVerificationRepository,
)
from tests.conftest import alembic_config

pytestmark = pytest.mark.db

TOMORROW = datetime.now(UTC) + timedelta(days=1)


@pytest.fixture
def user(db_session: Session) -> UserModel:
    user = UserModel(
        email="vecino@example.com", password_hash="hash", full_name="Alex", is_active=False
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def repository(db_session: Session) -> SqlAlchemyEmailVerificationRepository:
    return SqlAlchemyEmailVerificationRepository(db_session)


def stored(db_session: Session, token_hash: str) -> EmailVerificationModel:
    db_session.expire_all()
    return db_session.get_one(EmailVerificationModel, token_hash)


def test_link_cannot_be_used_and_superseded(db_session: Session, user: UserModel) -> None:
    db_session.add(
        EmailVerificationModel(
            token_hash="a" * 64,
            user_id=user.id,
            expires_at=TOMORROW,
            used_at=func.now(),
            superseded_at=func.now(),
        )
    )

    with pytest.raises(IntegrityError, match="ck_email_verification_used_or_superseded"):
        db_session.flush()


def link(user: UserModel, token_hash: str) -> EmailVerificationModel:
    return EmailVerificationModel(token_hash=token_hash, user_id=user.id, expires_at=TOMORROW)


def test_user_cannot_have_two_active_links(db_session: Session, user: UserModel) -> None:
    db_session.add(link(user, "a" * 64))
    db_session.flush()
    db_session.add(link(user, "b" * 64))

    with pytest.raises(IntegrityError, match="uq_email_verification_one_active_per_user"):
        db_session.flush()


def test_replace_supersedes_the_previous_link(
    db_session: Session, user: UserModel, repository: SqlAlchemyEmailVerificationRepository
) -> None:
    repository.replace(user.id, "a" * 64, TOMORROW)
    repository.replace(user.id, "b" * 64, TOMORROW)

    previous = repository.get("a" * 64)
    assert previous is not None
    assert previous.superseded_at is not None
    assert previous.used_at is None
    current = stored(db_session, "b" * 64)
    assert current.superseded_at is None
    assert current.used_at is None


def test_mark_used_supersedes_the_other_active_links(
    db_session: Session, user: UserModel, repository: SqlAlchemyEmailVerificationRepository
) -> None:
    repository.replace(user.id, "a" * 64, TOMORROW)
    repository.replace(user.id, "b" * 64, TOMORROW)

    repository.mark_used("b" * 64)

    used = stored(db_session, "b" * 64)
    assert used.used_at is not None
    assert used.superseded_at is None
    assert stored(db_session, "a" * 64).used_at is None
    active = select(func.count()).where(
        EmailVerificationModel.used_at.is_(None), EmailVerificationModel.superseded_at.is_(None)
    )
    assert db_session.scalar(active) == 0


def test_replace_purges_links_expired_more_than_30_days_ago(
    db_session: Session, user: UserModel, repository: SqlAlchemyEmailVerificationRepository
) -> None:
    now = datetime.now(UTC)
    repository.replace(user.id, "a" * 64, now - timedelta(days=31))
    repository.replace(user.id, "b" * 64, now - timedelta(days=29))

    repository.replace(user.id, "c" * 64, TOMORROW)

    db_session.expire_all()
    hashes = db_session.scalars(select(EmailVerificationModel.token_hash)).all()
    assert sorted(hashes) == ["b" * 64, "c" * 64]


def test_migration_0009_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0008")
        columns = {c["name"] for c in inspect(connection).get_columns("email_verification")}
        assert {"used_at", "superseded_at"}.isdisjoint(columns)

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        columns = {c["name"] for c in inspect(connection).get_columns("email_verification")}
        assert {"used_at", "superseded_at"} <= columns
