from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from entrevecinos.domain.mail.quota import QUOTA_TIMEZONE, current_period

MADRID = ZoneInfo("Europe/Madrid")


def madrid(*args: int) -> datetime:
    return datetime(*args, tzinfo=MADRID)


@pytest.mark.parametrize(
    ("now", "start", "end"),
    [
        (madrid(2026, 3, 20, 12), date(2026, 3, 6), date(2026, 4, 6)),
        (madrid(2026, 4, 5, 23, 59, 59), date(2026, 3, 6), date(2026, 4, 6)),
        (madrid(2026, 4, 6, 0, 0), date(2026, 4, 6), date(2026, 5, 6)),
        (madrid(2026, 12, 6, 0, 0), date(2026, 12, 6), date(2027, 1, 6)),
        (madrid(2027, 1, 3, 10), date(2026, 12, 6), date(2027, 1, 6)),
    ],
)
def test_period_from_day_6_to_day_6(now: datetime, start: date, end: date) -> None:
    period = current_period(now, reset_day=6)

    assert period.start == start
    assert period.ends_at == datetime(end.year, end.month, end.day, tzinfo=MADRID)


def test_period_uses_madrid_time_not_utc() -> None:
    # 5 de abril a las 22:30 UTC son las 00:30 del 6 en Madrid (horario de verano): periodo nuevo.
    assert current_period(datetime(2026, 4, 5, 22, 30, tzinfo=UTC), 6).start == date(2026, 4, 6)
    assert current_period(datetime(2026, 4, 5, 21, 59, tzinfo=UTC), 6).start == date(2026, 3, 6)


def test_default_timezone_is_madrid() -> None:
    assert QUOTA_TIMEZONE.key == "Europe/Madrid"


@pytest.mark.parametrize("reset_day", [0, 29])
def test_reset_day_must_exist_in_every_month(reset_day: int) -> None:
    with pytest.raises(ValueError):
        current_period(madrid(2026, 3, 1), reset_day)
