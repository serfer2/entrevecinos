"""Periodo del cupo de correos (TK-099): del día de reinicio de un mes al del mes siguiente."""

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

# Calendario del equipo: el periodo empieza a las 00:00 en hora de Madrid.
QUOTA_TIMEZONE = ZoneInfo("Europe/Madrid")


@dataclass(frozen=True, slots=True)
class QuotaPeriod:
    start: date
    """Fecha local en que empezó el periodo: identifica su contador."""
    ends_at: datetime
    """Inicio del periodo siguiente, con zona horaria."""


def _add_month(day: date) -> date:
    return date(day.year + day.month // 12, day.month % 12 + 1, day.day)


def _sub_month(day: date) -> date:
    return date(day.year - (day.month == 1), (day.month - 2) % 12 + 1, day.day)


def current_period(
    now: datetime, reset_day: int, timezone: ZoneInfo = QUOTA_TIMEZONE
) -> QuotaPeriod:
    """Periodo al que pertenece `now`: `[reset_day 00:00, mismo día del mes siguiente 00:00)`.

    Del día 1 al `reset_day - 1` cuenta el periodo que empezó el mes anterior. `reset_day` va de
    1 a 28, para que exista en todos los meses.
    """
    if not 1 <= reset_day <= 28:
        raise ValueError("reset_day debe estar entre 1 y 28")
    local = now.astimezone(timezone)
    start = date(local.year, local.month, reset_day)
    if local.date() < start:
        start = _sub_month(start)
    end = _add_month(start)
    return QuotaPeriod(start=start, ends_at=datetime.combine(end, time(0), tzinfo=timezone))
