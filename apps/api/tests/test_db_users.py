from datetime import timedelta

import pytest
from alembic import command
from sqlalchemy import Engine, delete, func, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import EmailVerificationModel, UserModel
from tests.conftest import alembic_config

pytestmark = pytest.mark.db


def make_user(**overrides: object) -> UserModel:
    values = {
        "email": "vecino@example.com",
        "password_hash": "hash",
        "full_name": "Alex Vecino",
        "email_verified_at": func.now(),
    }
    return UserModel(**{**values, **overrides})


def test_minimal_insert_applies_defaults(db_session: Session) -> None:
    db_session.add(make_user())
    db_session.flush()

    user = db_session.scalars(select(UserModel)).one()
    db_session.refresh(user)

    assert user.id is not None
    assert user.platform_role == "user"
    assert user.is_active is True
    assert user.created_at.utcoffset() == timedelta(0)
    assert user.updated_at.utcoffset() == timedelta(0)
    assert user.phone is None
    assert user.avatar_asset_id is None
    assert user.deleted_at is None


def test_duplicate_email_is_rejected(db_session: Session) -> None:
    db_session.add(make_user())
    db_session.flush()
    db_session.add(make_user(full_name="Otra persona"))

    with pytest.raises(IntegrityError, match="uq_users_email"):
        db_session.flush()


def test_uppercase_email_is_rejected(db_session: Session) -> None:
    db_session.add(make_user(email="Vecino@Example.com"))

    with pytest.raises(IntegrityError, match="ck_users_email_lowercase"):
        db_session.flush()


@pytest.mark.parametrize("full_name", ["", "   "])
def test_blank_full_name_is_rejected(db_session: Session, full_name: str) -> None:
    db_session.add(make_user(full_name=full_name))

    with pytest.raises(IntegrityError, match="ck_users_full_name_not_blank"):
        db_session.flush()


def test_active_user_requires_verified_email(db_session: Session) -> None:
    db_session.add(make_user(email_verified_at=None))

    with pytest.raises(IntegrityError, match="ck_users_active_requires_verified_email"):
        db_session.flush()


def test_inactive_user_may_be_unverified(db_session: Session) -> None:
    db_session.add(make_user(email_verified_at=None, is_active=False))
    db_session.flush()


def test_platform_admin_may_be_active_unverified(db_session: Session) -> None:
    db_session.add(make_user(email_verified_at=None, platform_role="platform_admin"))
    db_session.flush()


def test_deleting_a_user_deletes_its_verifications(db_session: Session) -> None:
    user = make_user(email_verified_at=None, is_active=False)
    db_session.add(user)
    db_session.flush()
    db_session.add(
        EmailVerificationModel(token_hash="a" * 64, user_id=user.id, expires_at=func.now())
    )
    db_session.flush()

    db_session.execute(delete(UserModel).where(UserModel.id == user.id))

    assert db_session.scalars(select(EmailVerificationModel)).all() == []


def test_migration_0008_marks_existing_users_as_verified(db_engine: Engine) -> None:
    with db_engine.connect() as connection:
        transaction = connection.begin()
        try:
            command.downgrade(alembic_config(connection), "0007")
            connection.execute(
                text(
                    "INSERT INTO users (email, password_hash, full_name, created_at) "
                    "VALUES ('antes@example.com', 'hash', 'Alex', '2026-01-01T00:00:00Z')"
                )
            )
            command.upgrade(alembic_config(connection), "head")

            row = connection.execute(
                text("SELECT is_active, email_verified_at, created_at FROM users")
            ).one()
            assert row.is_active is True
            assert row.email_verified_at == row.created_at
        finally:
            transaction.rollback()


def test_migrations_are_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0007")
        assert not inspect(connection).has_table("email_verification")
        assert "email_verified_at" not in {
            c["name"] for c in inspect(connection).get_columns("users")
        }
        command.downgrade(alembic_config(connection), "base")
        assert not inspect(connection).has_table("users")

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        assert inspect(connection).has_table("users")
