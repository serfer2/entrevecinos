import uuid
from datetime import datetime, timedelta

from sqlalchemy import ColumnElement, delete, func, select, update
from sqlalchemy.orm import Session

from entrevecinos.domain.users.entities import EmailVerification
from entrevecinos.infrastructure.db.models import EmailVerificationModel

# Pasado este tiempo desde su caducidad, un enlace se borra y vuelve a ser desconocido.
RETENTION = timedelta(days=30)


def _active(user_id: uuid.UUID) -> ColumnElement[bool]:
    return (
        (EmailVerificationModel.user_id == user_id)
        & EmailVerificationModel.used_at.is_(None)
        & EmailVerificationModel.superseded_at.is_(None)
    )


class SqlAlchemyEmailVerificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def replace(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        self._session.execute(
            delete(EmailVerificationModel).where(
                EmailVerificationModel.user_id == user_id,
                EmailVerificationModel.expires_at < func.now() - RETENTION,
            )
        )
        self._session.execute(
            update(EmailVerificationModel).where(_active(user_id)).values(superseded_at=func.now())
        )
        self._session.add(
            EmailVerificationModel(token_hash=token_hash, user_id=user_id, expires_at=expires_at)
        )
        self._session.flush()

    def get(self, token_hash: str) -> EmailVerification | None:
        model = self._session.get(EmailVerificationModel, token_hash)
        if model is None:
            return None
        return EmailVerification(
            user_id=model.user_id,
            expires_at=model.expires_at,
            created_at=model.created_at,
            used_at=model.used_at,
            superseded_at=model.superseded_at,
        )

    def last_created_at(self, user_id: uuid.UUID) -> datetime | None:
        return self._session.scalar(
            select(func.max(EmailVerificationModel.created_at)).where(
                EmailVerificationModel.user_id == user_id
            )
        )

    def mark_used(self, token_hash: str) -> None:
        user_id = self._session.scalar(
            select(EmailVerificationModel.user_id).where(
                EmailVerificationModel.token_hash == token_hash
            )
        )
        if user_id is None:
            return
        self._session.execute(
            update(EmailVerificationModel)
            .where(_active(user_id), EmailVerificationModel.token_hash != token_hash)
            .values(superseded_at=func.now())
        )
        self._session.execute(
            update(EmailVerificationModel)
            .where(EmailVerificationModel.token_hash == token_hash)
            .values(used_at=func.now())
        )
