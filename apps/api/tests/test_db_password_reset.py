from datetime import UTC, datetime, timedelta

import pytest
from alembic import command
from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import PasswordResetModel, UserModel
from entrevecinos.infrastructure.users.sqlalchemy_password_reset_repository import (
    SqlAlchemyPasswordResetRepository,
)
from entrevecinos.infrastructure.users.sqlalchemy_user_repository import SqlAlchemyUserRepository
from tests.conftest import alembic_config

pytestmark = pytest.mark.db

IN_ONE_HOUR = datetime.now(UTC) + timedelta(hours=1)


@pytest.fixture
def user(db_session: Session) -> UserModel:
    user = UserModel(email="vecino@example.com", password_hash="hash", full_name="Alex")
    user.email_verified_at = datetime.now(UTC)
    db_session.add(user)
    db_session.flush()
    return user


def test_new_users_have_not_changed_their_password(db_session: Session, user: UserModel) -> None:
    db_session.expire_all()

    assert db_session.get_one(UserModel, user.id).password_changed_at is None


def test_link_stores_only_the_hash_and_its_creation_date(
    db_session: Session, user: UserModel
) -> None:
    db_session.add(PasswordResetModel(token_hash="a" * 64, user_id=user.id, expires_at=IN_ONE_HOUR))
    db_session.flush()
    db_session.expire_all()

    stored = db_session.get_one(PasswordResetModel, "a" * 64)
    assert stored.user_id == user.id
    assert stored.created_at is not None


def test_deleting_the_user_deletes_its_links(db_session: Session, user: UserModel) -> None:
    db_session.add(PasswordResetModel(token_hash="a" * 64, user_id=user.id, expires_at=IN_ONE_HOUR))
    db_session.flush()

    db_session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})

    assert db_session.scalars(select(PasswordResetModel)).all() == []


def test_migration_0011_is_reversible_and_keeps_existing_users(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0010")
        assert not inspect(connection).has_table("password_reset")
        columns = {c["name"] for c in inspect(connection).get_columns("users")}
        assert "password_changed_at" not in columns
        connection.execute(
            text(
                "INSERT INTO users (email, password_hash, full_name, email_verified_at) "
                "VALUES ('antes@example.com', 'hash-anterior', 'Antes', now())"
            )
        )

    try:
        with db_engine.begin() as connection:
            command.upgrade(alembic_config(connection), "head")
            assert inspect(connection).has_table("password_reset")
            row = connection.execute(
                text(
                    "SELECT password_hash, password_changed_at FROM users "
                    "WHERE email = 'antes@example.com'"
                )
            ).one()
            assert row.password_hash == "hash-anterior"
            assert row.password_changed_at is None
    finally:
        with db_engine.begin() as connection:
            connection.execute(text("DELETE FROM users WHERE email = 'antes@example.com'"))


def test_replace_deletes_the_previous_links_of_the_user(
    db_session: Session, user: UserModel
) -> None:
    other = UserModel(email="otro@example.com", password_hash="hash", full_name="Otro")
    other.email_verified_at = datetime.now(UTC)
    db_session.add(other)
    db_session.flush()
    repository = SqlAlchemyPasswordResetRepository(db_session)
    repository.replace(other.id, "c" * 64, IN_ONE_HOUR)

    repository.replace(user.id, "a" * 64, IN_ONE_HOUR)
    repository.replace(user.id, "b" * 64, IN_ONE_HOUR)

    assert repository.get("a" * 64) is None
    stored = repository.get("b" * 64)
    assert stored is not None
    assert stored.user_id == user.id
    assert stored.expires_at == IN_ONE_HOUR
    assert repository.get("c" * 64) is not None


def test_last_created_at(db_session: Session, user: UserModel) -> None:
    repository = SqlAlchemyPasswordResetRepository(db_session)
    assert repository.last_created_at(user.id) is None

    repository.replace(user.id, "a" * 64, IN_ONE_HOUR)

    assert repository.last_created_at(user.id) is not None


def test_delete_for_user_deletes_only_its_links(db_session: Session, user: UserModel) -> None:
    other = UserModel(email="otro@example.com", password_hash="hash", full_name="Otro")
    other.email_verified_at = datetime.now(UTC)
    db_session.add(other)
    db_session.flush()
    repository = SqlAlchemyPasswordResetRepository(db_session)
    repository.replace(user.id, "a" * 64, IN_ONE_HOUR)
    repository.replace(other.id, "b" * 64, IN_ONE_HOUR)

    repository.delete_for_user(user.id)

    assert repository.get("a" * 64) is None
    assert repository.get("b" * 64) is not None


def test_change_password_sets_the_change_date_and_rehash_does_not(
    db_session: Session, user: UserModel
) -> None:
    repository = SqlAlchemyUserRepository(db_session)

    repository.update_password_hash(user.id, "hash-reescrito")
    assert repository.get_by_id(user.id).password_changed_at is None

    repository.change_password(user.id, "hash-nuevo")
    db_session.expire_all()

    stored = db_session.get_one(UserModel, user.id)
    assert stored.password_hash == "hash-nuevo"
    assert repository.get_by_id(user.id).password_changed_at is not None
