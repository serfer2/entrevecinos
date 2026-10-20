import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, pool, text
from sqlalchemy.orm import Session

# `presentation.main` crea la app al importarse; las pruebas necesitan una configuración mínima.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret-with-at-least-32-characters")
for _name, _value in {
    "STORAGE_ENDPOINT": "http://storage:9000",
    "STORAGE_PUBLIC_ENDPOINT": "http://localhost:9000",
    "STORAGE_BUCKET": "test-bucket",
    "STORAGE_ACCESS_KEY": "test-access-key",
    "STORAGE_SECRET_KEY": "test-secret-key",
}.items():
    os.environ.setdefault(_name, _value)

TEST_JWT_SECRET = "test-secret-with-at-least-32-characters-!!"

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def alembic_config(connection) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.attributes["connection"] = connection
    return config


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    """Base de datos `<db>_test`, creada si no existe y migrada a la última versión."""
    dev_url = make_url(os.environ["DATABASE_URL"])
    test_url = dev_url.set(database=f"{dev_url.database}_test")

    admin = create_engine(dev_url, isolation_level="AUTOCOMMIT", poolclass=pool.NullPool)
    with admin.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": test_url.database}
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    admin.dispose()

    engine = create_engine(test_url, poolclass=pool.NullPool)
    with engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    """Sesión dentro de una transacción que se revierte al terminar cada prueba.

    Los `commit()` del código bajo prueba solo liberan *savepoints*.
    """
    with db_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


def make_settings(**overrides: object):
    from entrevecinos.infrastructure.settings import Settings

    values = {"database_url": os.environ["DATABASE_URL"], "jwt_secret": TEST_JWT_SECRET}
    return Settings(**{**values, **overrides})


def _fast_hasher():
    from pwdlib.hashers.argon2 import Argon2Hasher

    from entrevecinos.infrastructure.security.password_hasher import Argon2PasswordHasher

    return Argon2PasswordHasher(Argon2Hasher(time_cost=1, memory_cost=1024, parallelism=1))


FAST_HASHER = _fast_hasher()


@pytest.fixture
def object_storage():
    """Almacenamiento de objetos en memoria (la prueba `storage` usa MinIO real)."""
    from tests.fakes import InMemoryObjectStorage

    return InMemoryObjectStorage()


@pytest.fixture
def client(db_session: Session, object_storage) -> TestClient:
    """Cliente HTTP cuya sesión de base de datos es la transacción de la prueba."""
    from entrevecinos.infrastructure.db.session import get_session
    from entrevecinos.presentation.dependencies import get_object_storage, get_password_hasher
    from entrevecinos.presentation.main import create_app

    app = create_app(make_settings())
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_object_storage] = lambda: object_storage
    # Argon2id con un coste mínimo: el algoritmo es el mismo, pero las pruebas no esperan.
    app.dependency_overrides[get_password_hasher] = lambda: FAST_HASHER
    return TestClient(app)
