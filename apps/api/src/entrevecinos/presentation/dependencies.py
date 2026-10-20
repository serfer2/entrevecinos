from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.users.authenticate_user import AuthenticateUser
from entrevecinos.application.users.get_current_user import GetCurrentUser
from entrevecinos.application.users.register_user import RegisterUser
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import NotAuthenticated
from entrevecinos.infrastructure.communities.sqlalchemy_community_repository import (
    SqlAlchemyCommunityRepository,
)
from entrevecinos.infrastructure.communities.sqlalchemy_membership_repository import (
    SqlAlchemyMembershipRepository,
)
from entrevecinos.infrastructure.db.session import get_session
from entrevecinos.infrastructure.media.sqlalchemy_media_repository import (
    SqlAlchemyMediaRepository,
)
from entrevecinos.infrastructure.security.jwt_tokens import JwtTokenService
from entrevecinos.infrastructure.security.password_hasher import Argon2PasswordHasher
from entrevecinos.infrastructure.settings import Settings, get_settings
from entrevecinos.infrastructure.storage.s3_object_storage import S3ObjectStorage
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


def get_membership_repository(session: SessionDep) -> SqlAlchemyMembershipRepository:
    return SqlAlchemyMembershipRepository(session)


def get_community_repository(session: SessionDep) -> SqlAlchemyCommunityRepository:
    return SqlAlchemyCommunityRepository(session)


UserRepositoryDep = Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)]
CommunityRepositoryDep = Annotated[SqlAlchemyCommunityRepository, Depends(get_community_repository)]
MembershipRepositoryDep = Annotated[
    SqlAlchemyMembershipRepository, Depends(get_membership_repository)
]
PasswordHasherDep = Annotated[Argon2PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[JwtTokenService, Depends(get_token_service)]


def get_register_user(
    users: UserRepositoryDep, hasher: PasswordHasherDep, tokens: TokenServiceDep
) -> RegisterUser:
    return RegisterUser(users, hasher, tokens)


def get_authenticate_user(
    users: UserRepositoryDep, hasher: PasswordHasherDep, tokens: TokenServiceDep
) -> AuthenticateUser:
    return AuthenticateUser(users, hasher, tokens)


# auto_error=False: los fallos los responde NotAuthenticated, con el mismo cuerpo siempre.
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="bearerAuth", bearerFormat="JWT")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    users: UserRepositoryDep,
    tokens: TokenServiceDep,
) -> User:
    """Usuario de `Authorization: Bearer <token>`. Única forma de proteger endpoints."""
    if credentials is None:
        raise NotAuthenticated
    return GetCurrentUser(users).execute(tokens.decode(credentials.credentials))


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_community_access(
    communities: CommunityRepositoryDep, memberships: MembershipRepositoryDep
) -> CommunityAccess:
    return CommunityAccess(communities, memberships)


CommunityAccessDep = Annotated[CommunityAccess, Depends(get_community_access)]


def get_media_repository(session: SessionDep) -> SqlAlchemyMediaRepository:
    return SqlAlchemyMediaRepository(session)


@lru_cache
def _object_storage(
    endpoint: str, public_endpoint: str, bucket: str, access_key: str, secret_key: str
) -> S3ObjectStorage:
    # Los clientes de boto3 son costosos de crear y seguros entre hilos: uno por configuración.
    return S3ObjectStorage(endpoint, public_endpoint, bucket, access_key, secret_key)


def get_object_storage(settings: SettingsDep) -> S3ObjectStorage:
    return _object_storage(
        settings.storage_endpoint,
        settings.storage_public_endpoint,
        settings.storage_bucket,
        settings.storage_access_key,
        settings.storage_secret_key,
    )


MediaRepositoryDep = Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)]
ObjectStorageDep = Annotated[S3ObjectStorage, Depends(get_object_storage)]
