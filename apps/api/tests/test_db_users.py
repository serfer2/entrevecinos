from datetime import timedelta

import pytest
from alembic import command
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import UserModel
from tests.conftest import alembic_config

pytestmark = pytest.mark.db


def make_user(**overrides: object) -> UserModel:
    values = {"email": "vecino@example.com", "password_hash": "hash", "full_name": "Alex Vecino"}
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


def test_migrations_are_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "base")
        assert not inspect(connection).has_table("users")

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        assert inspect(connection).has_table("users")
