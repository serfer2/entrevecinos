from datetime import date

import pytest
from alembic import command
from sqlalchemy import Engine, inspect
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.mail.sqlalchemy_email_quota_repository import (
    SqlAlchemyEmailQuotaRepository,
)
from tests.conftest import alembic_config

pytestmark = pytest.mark.db

PERIOD = date(2026, 3, 6)


def test_reserves_until_the_limit_and_then_returns_none(db_session: Session) -> None:
    repository = SqlAlchemyEmailQuotaRepository(db_session)

    assert repository.sent(PERIOD) == 0
    assert [repository.reserve(PERIOD, 3) for _ in range(4)] == [1, 2, 3, None]
    assert repository.sent(PERIOD) == 3


def test_last_place_of_5000_is_granted_and_the_next_is_not(db_session: Session) -> None:
    repository = SqlAlchemyEmailQuotaRepository(db_session)
    for _ in range(4999):
        repository.reserve(PERIOD, 5000)

    assert repository.reserve(PERIOD, 5000) == 5000
    assert repository.reserve(PERIOD, 5000) is None


def test_each_period_has_its_own_counter(db_session: Session) -> None:
    repository = SqlAlchemyEmailQuotaRepository(db_session)
    repository.reserve(PERIOD, 1)

    assert repository.reserve(PERIOD, 1) is None
    assert repository.reserve(date(2026, 4, 6), 1) == 1


def test_migration_0010_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        config = alembic_config(connection)
        command.downgrade(config, "0009")
        assert "email_quota" not in inspect(connection).get_table_names()
        command.upgrade(config, "head")
        assert "email_quota" in inspect(connection).get_table_names()


def test_two_concurrent_requests_cannot_take_the_last_place(db_engine: Engine) -> None:
    """Con una plaza libre, la segunda transacción espera a la primera y no obtiene plaza."""
    import threading

    from sqlalchemy import delete

    from entrevecinos.infrastructure.db.models import EmailQuotaModel

    period = date(2099, 1, 6)  # Fuera de cualquier periodo real; se borra al terminar.
    first, second = Session(db_engine), Session(db_engine)
    try:
        first_repository = SqlAlchemyEmailQuotaRepository(first)
        for _ in range(2):
            first_repository.reserve(period, 3)
        first.commit()

        assert first_repository.reserve(period, 3) == 3  # Última plaza, sin confirmar aún.
        results: list[int | None] = []
        waiting = threading.Thread(
            target=lambda: results.append(SqlAlchemyEmailQuotaRepository(second).reserve(period, 3))
        )
        waiting.start()
        waiting.join(timeout=1)
        assert waiting.is_alive()  # Bloqueada por la fila de la primera transacción.

        first.commit()
        waiting.join(timeout=10)
        assert results == [None]
    finally:
        second.rollback()
        with Session(db_engine) as cleanup:
            cleanup.execute(delete(EmailQuotaModel).where(EmailQuotaModel.period_start == period))
            cleanup.commit()
        first.close()
        second.close()
