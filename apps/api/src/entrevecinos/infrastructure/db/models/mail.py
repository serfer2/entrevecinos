from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column

from entrevecinos.infrastructure.db.base import Base


class EmailQuotaModel(Base):
    """Correos enviados en cada periodo del cupo (TK-099): una fila por periodo."""

    __tablename__ = "email_quota"
    __table_args__ = (CheckConstraint("sent >= 0", name="sent_not_negative"),)

    period_start: Mapped[date] = mapped_column(Date, primary_key=True)
    sent: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
