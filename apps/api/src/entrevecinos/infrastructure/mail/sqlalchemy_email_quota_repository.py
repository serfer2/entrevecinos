from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import EmailQuotaModel


class SqlAlchemyEmailQuotaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def sent(self, period_start: date) -> int:
        value = self._session.scalar(
            select(EmailQuotaModel.sent).where(EmailQuotaModel.period_start == period_start)
        )
        return value or 0

    def reserve(self, period_start: date, limit: int) -> int | None:
        # Una sola sentencia: el bloqueo de la fila serializa las peticiones concurrentes y la
        # condición se vuelve a evaluar con el valor ya confirmado por la otra transacción.
        statement = (
            insert(EmailQuotaModel)
            .values(period_start=period_start, sent=1)
            .on_conflict_do_update(
                index_elements=[EmailQuotaModel.period_start],
                set_={"sent": EmailQuotaModel.sent + 1, "updated_at": func.now()},
                where=EmailQuotaModel.sent < limit,
            )
            .returning(EmailQuotaModel.sent)
        )
        return self._session.execute(statement).scalar_one_or_none()
