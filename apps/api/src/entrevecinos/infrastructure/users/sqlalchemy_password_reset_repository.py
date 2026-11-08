import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from entrevecinos.domain.users.entities import PasswordReset
from entrevecinos.infrastructure.db.models import PasswordResetModel


class SqlAlchemyPasswordResetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def replace(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        self._session.execute(
            delete(PasswordResetModel).where(PasswordResetModel.user_id == user_id)
        )
        self._session.add(
            PasswordResetModel(token_hash=token_hash, user_id=user_id, expires_at=expires_at)
        )
        self._session.flush()

    def get(self, token_hash: str) -> PasswordReset | None:
        model = self._session.get(PasswordResetModel, token_hash)
        if model is None:
            return None
        return PasswordReset(
            user_id=model.user_id, expires_at=model.expires_at, created_at=model.created_at
        )

    def last_created_at(self, user_id: uuid.UUID) -> datetime | None:
        return self._session.scalar(
            select(func.max(PasswordResetModel.created_at)).where(
                PasswordResetModel.user_id == user_id
            )
        )
