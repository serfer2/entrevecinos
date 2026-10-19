from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from entrevecinos.application.users.register_user import RegisterUser
from entrevecinos.infrastructure.db.session import get_session
from entrevecinos.infrastructure.security.jwt_tokens import JwtTokenService
from entrevecinos.infrastructure.security.password_hasher import Argon2PasswordHasher
from entrevecinos.infrastructure.settings import Settings, get_settings
from entrevecinos.infrastructure.users.sqlalchemy_user_repository import SqlAlchemyUserRepository

SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_user_repository(session: SessionDep) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


@lru_cache
def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


def get_token_service(settings: SettingsDep) -> JwtTokenService:
    return JwtTokenService(settings.jwt_secret, settings.jwt_ttl_seconds)


UserRepositoryDep = Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[Argon2PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[JwtTokenService, Depends(get_token_service)]


def get_register_user(
    users: UserRepositoryDep, hasher: PasswordHasherDep, tokens: TokenServiceDep
) -> RegisterUser:
    return RegisterUser(users, hasher, tokens)
