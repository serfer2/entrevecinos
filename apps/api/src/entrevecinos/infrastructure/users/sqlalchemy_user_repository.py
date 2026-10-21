import uuid
from collections.abc import Mapping

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from entrevecinos.domain.users.errors import EmailAlreadyRegistered
from entrevecinos.infrastructure.db.models import UserModel


def to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        full_name=model.full_name,
        phone=model.phone,
        platform_role=PlatformRole(model.platform_role),
        is_active=model.is_active,
        created_at=model.created_at,
        deleted_at=model.deleted_at,
        email_verified_at=model.email_verified_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        model = self._session.get(UserModel, user_id)
        return to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalars(select(UserModel).where(UserModel.email == email)).first()
        return to_domain(model) if model else None

    def get_credentials(self, email: str) -> tuple[User, str] | None:
        model = self._session.scalars(select(UserModel).where(UserModel.email == email)).first()
        return (to_domain(model), model.password_hash) if model else None

    def add(self, user: NewUser, password_hash: str) -> User:
        model = UserModel(
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            password_hash=password_hash,
            # Se activa al validar el correo (HU-25).
            is_active=False,
        )
        try:
            # El savepoint permite seguir usando la sesión si falla la restricción.
            with self._session.begin_nested():
                self._session.add(model)
        except IntegrityError as error:
            if "uq_users_email" in str(error.orig):
                raise EmailAlreadyRegistered(user.email) from error
            raise
        self._session.refresh(model)
        return to_domain(model)

    def mark_email_verified(self, user_id: uuid.UUID) -> User:
        model = self._session.get_one(UserModel, user_id)
        model.email_verified_at = func.now()
        model.is_active = True
        self._session.flush()
        self._session.refresh(model)
        return to_domain(model)

    def update_password_hash(self, user_id: uuid.UUID, password_hash: str) -> None:
        self._session.execute(
            update(UserModel).where(UserModel.id == user_id).values(password_hash=password_hash)
        )

    def update_profile(self, user_id: uuid.UUID, values: Mapping[str, str | None]) -> User:
        model = self._session.get_one(UserModel, user_id)
        for field, value in values.items():
            setattr(model, field, value)
        self._session.flush()
        self._session.refresh(model)
        return to_domain(model)
