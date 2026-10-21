import uuid
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from entrevecinos.domain.users.entities import EmailVerification
from entrevecinos.infrastructure.db.models import EmailVerificationModel


class SqlAlchemyEmailVerificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def replace(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        self.delete_for_user(user_id)
        self._session.add(
            EmailVerificationModel(token_hash=token_hash, user_id=user_id, expires_at=expires_at)
        )
        self._session.flush()

    def get(self, token_hash: str) -> EmailVerification | None:
        model = self._session.get(EmailVerificationModel, token_hash)
        if model is None:
            return None
        return EmailVerification(
            user_id=model.user_id, expires_at=model.expires_at, created_at=model.created_at
        )

    def delete_for_user(self, user_id: uuid.UUID) -> None:
        self._session.execute(
            delete(EmailVerificationModel).where(EmailVerificationModel.user_id == user_id)
        )
