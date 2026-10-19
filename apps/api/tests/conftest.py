import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, make_url, pool, text
from sqlalchemy.orm import Session

# `presentation.main` crea la app al importarse; las pruebas necesitan una configuración mínima.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")

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
