from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine, pool

from entrevecinos.infrastructure.db import models  # noqa: F401  (registra los modelos)
from entrevecinos.infrastructure.db.base import Base
from entrevecinos.infrastructure.settings import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Las pruebas pasan su propia conexión para migrar la base de datos de pruebas.
    connection = config.attributes.get("connection")
    if connection is not None:
        run_migrations(connection)
        return

    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
