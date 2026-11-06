"""Cupo de correos por periodo (TK-099). Es una restricción de costes: el correo no puede pasar
del plan más barato del proveedor ni sacar el gasto del límite mensual (ver infra/aws/README.md)."""

import logging
import math
from datetime import date
from typing import Protocol
from zoneinfo import ZoneInfo

from entrevecinos.application.users.email_verification import Clock, utc_now
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.mail.quota import QUOTA_TIMEZONE, QuotaPeriod, current_period

logger = logging.getLogger(__name__)

# Las alarmas de producción buscan estos textos en el registro de la API (TK-099).
WARNING_MESSAGE = "Cupo de correo al 80 %%: %d de %d en el periodo que empezó el %s"
EXCEEDED_MESSAGE = "Límite mensual de correos alcanzado: %d en el periodo que empezó el %s"


class EmailQuotaRepository(Protocol):
    def sent(self, period_start: date) -> int:
        """Correos enviados en el periodo (0 si aún no hay ninguno)."""
        ...

    def reserve(self, period_start: date, limit: int) -> int | None:
        """Suma un correo al periodo si no ha llegado a `limit`, de forma atómica.

        Devuelve el contador nuevo, o `None` si ya estaba en el límite.
        """
        ...


class EmailQuota:
    """Comprueba y reserva plazas del cupo antes de enviar un correo."""

    def __init__(
        self,
        repository: EmailQuotaRepository,
        limit: int,
        reset_day: int,
        timezone: ZoneInfo = QUOTA_TIMEZONE,
        clock: Clock = utc_now,
    ) -> None:
        self._repository = repository
        self._limit = limit
        self._reset_day = reset_day
        self._timezone = timezone
        self._clock = clock
        self._warning_at = math.ceil(limit * 0.8)

    def ensure_available(self) -> None:
        """Lanza `EmailQuotaExceeded` si no queda cupo, sin reservar nada."""
        period = self._period()
        if self._repository.sent(period.start) >= self._limit:
            self._exceeded(period)

    def reserve(self) -> None:
        """Reserva una plaza para un correo o lanza `EmailQuotaExceeded`."""
        period = self._period()
        sent = self._repository.reserve(period.start, self._limit)
        if sent is None:
            self._exceeded(period)
        if sent == self._warning_at:
            logger.warning(WARNING_MESSAGE, sent, self._limit, period.start.isoformat())

    def _period(self) -> QuotaPeriod:
        return current_period(self._clock(), self._reset_day, self._timezone)

    def _exceeded(self, period: QuotaPeriod) -> None:
        logger.error(EXCEEDED_MESSAGE, self._limit, period.start.isoformat())
        seconds = math.ceil((period.ends_at - self._clock()).total_seconds())
        raise EmailQuotaExceeded(retry_after_seconds=max(seconds, 1))
