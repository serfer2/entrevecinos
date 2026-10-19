from sqlalchemy import select
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
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalars(select(UserModel).where(UserModel.email == email)).first()
        return to_domain(model) if model else None

    def add(self, user: NewUser, password_hash: str) -> User:
        model = UserModel(
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            password_hash=password_hash,
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
