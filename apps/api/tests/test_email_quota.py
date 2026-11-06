import logging
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from tests.fakes import InMemoryEmailQuotaRepository

# 20 de marzo de 2026 a mediodía en Madrid: periodo del 6 de marzo al 6 de abril.
NOW = datetime(2026, 3, 20, 11, 0, tzinfo=UTC)
PERIOD = date(2026, 3, 6)


def quota(counts: InMemoryEmailQuotaRepository, limit: int = 5, now: datetime = NOW) -> EmailQuota:
    return EmailQuota(counts, limit, reset_day=6, clock=lambda: now)


def test_reserves_until_the_limit() -> None:
    counts = InMemoryEmailQuotaRepository()
    for _ in range(5):
        quota(counts).reserve()

    with pytest.raises(EmailQuotaExceeded):
        quota(counts).reserve()
    assert counts.counts == {PERIOD: 5}


def test_retry_after_lasts_until_the_next_period() -> None:
    counts = InMemoryEmailQuotaRepository()
    counts.counts[PERIOD] = 5

    with pytest.raises(EmailQuotaExceeded) as error:
        quota(counts).reserve()

    next_period = datetime(2026, 4, 6, tzinfo=ZoneInfo("Europe/Madrid"))
    assert error.value.retry_after_seconds == int((next_period - NOW).total_seconds())


def test_new_period_starts_from_zero() -> None:
    counts = InMemoryEmailQuotaRepository()
    counts.counts[PERIOD] = 5

    quota(counts, now=datetime(2026, 4, 6, 0, 30, tzinfo=ZoneInfo("Europe/Madrid"))).reserve()

    assert counts.counts[date(2026, 4, 6)] == 1


def test_ensure_available_does_not_reserve() -> None:
    counts = InMemoryEmailQuotaRepository()
    quota(counts).ensure_available()
    assert counts.counts == {}

    counts.counts[PERIOD] = 5
    with pytest.raises(EmailQuotaExceeded):
        quota(counts).ensure_available()


def test_logs_warning_at_80_percent_once_and_error_when_blocked(
    caplog: pytest.LogCaptureFixture,
) -> None:
    counts = InMemoryEmailQuotaRepository()
    with caplog.at_level(logging.WARNING, logger="entrevecinos.application.mail.email_quota"):
        for _ in range(5):
            quota(counts).reserve()
        with pytest.raises(EmailQuotaExceeded):
            quota(counts).reserve()

    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    errors = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert warnings == ["Cupo de correo al 80 %: 4 de 5 en el periodo que empezó el 2026-03-06"]
    assert errors == [
        "Límite mensual de correos alcanzado: 5 en el periodo que empezó el 2026-03-06"
    ]
    assert "@" not in " ".join(warnings + errors)
