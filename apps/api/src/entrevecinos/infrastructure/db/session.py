from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from entrevecinos.infrastructure.settings import get_settings

SessionLocal = sessionmaker(expire_on_commit=False)


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Sesión por petición: confirma al terminar y revierte si hay una excepción."""
    session = SessionLocal(bind=get_engine())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
