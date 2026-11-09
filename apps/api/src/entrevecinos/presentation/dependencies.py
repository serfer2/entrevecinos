from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.communities.community_notices import CommunityNotices
from entrevecinos.application.communities.membership_notices import MembershipNotices
from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.authenticate_user import AuthenticateUser
from entrevecinos.application.users.email_verification import EmailVerificationIssuer
from entrevecinos.application.users.get_current_user import GetCurrentUser
from entrevecinos.application.users.password_reset import PasswordResetIssuer
from entrevecinos.application.users.ports import EmailSender
from entrevecinos.application.users.register_user import RegisterUser
from entrevecinos.application.users.request_password_reset import RequestPasswordReset
from entrevecinos.application.users.resend_email_verification import ResendEmailVerification
from entrevecinos.application.users.reset_password import ResetPassword
from entrevecinos.application.users.verify_email import VerifyEmail
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import NotAuthenticated
from entrevecinos.infrastructure.communities.sqlalchemy_community_repository import (
    SqlAlchemyCommunityRepository,
)
from entrevecinos.infrastructure.communities.sqlalchemy_membership_repository import (
    SqlAlchemyMembershipRepository,
)
from entrevecinos.infrastructure.db.session import get_session
from entrevecinos.infrastructure.listings.sqlalchemy_category_repository import (
    SqlAlchemyCategoryRepository,
)
from entrevecinos.infrastructure.listings.sqlalchemy_listing_repository import (
    SqlAlchemyListingRepository,
)
from entrevecinos.infrastructure.mail.ses_email_sender import SesEmailSender
from entrevecinos.infrastructure.mail.smtp_email_sender import SmtpEmailSender
from entrevecinos.infrastructure.mail.sqlalchemy_email_quota_repository import (
    SqlAlchemyEmailQuotaRepository,
)
from entrevecinos.infrastructure.media.sqlalchemy_media_repository import (
    SqlAlchemyMediaRepository,
)
from entrevecinos.infrastructure.security.jwt_tokens import JwtTokenService
from entrevecinos.infrastructure.security.password_hasher import Argon2PasswordHasher
from entrevecinos.infrastructure.settings import Settings, get_settings
from entrevecinos.infrastructure.storage.s3_object_storage import S3ObjectStorage
from entrevecinos.infrastructure.users.sqlalchemy_email_verification_repository import (
    SqlAlchemyEmailVerificationRepository,
)
from entrevecinos.infrastructure.users.sqlalchemy_password_reset_repository import (
    SqlAlchemyPasswordResetRepository,
)
from entrevecinos.infrastructure.users.sqlalchemy_user_repository import SqlAlchemyUserRepository

# scope="function": la transacción se confirma al terminar el endpoint, antes de responder y antes
# de las tareas en segundo plano. Con el ámbito por defecto se confirmaría después de enviar los
# correos, y la web leería los datos sin confirmar al recargar (p. ej. «Solicitar acceso»).
SessionDep = Annotated[Session, Depends(get_session, scope="function")]
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


def get_email_verification_repository(session: SessionDep) -> SqlAlchemyEmailVerificationRepository:
    return SqlAlchemyEmailVerificationRepository(session)


EmailVerificationRepositoryDep = Annotated[
    SqlAlchemyEmailVerificationRepository, Depends(get_email_verification_repository)
]


@lru_cache
def _ses_email_sender(sender: str, region: str, configuration_set: str) -> SesEmailSender:
    # Un cliente de boto3 por configuración, como el almacenamiento.
    return SesEmailSender(sender, region, configuration_set=configuration_set)


def get_email_sender(settings: SettingsDep) -> EmailSender:
    if settings.mail_backend == "ses":
        return _ses_email_sender(
            settings.mail_from, settings.ses_region, settings.ses_configuration_set
        )
    return SmtpEmailSender(
        settings.smtp_host,
        settings.smtp_port,
        settings.mail_from,
        username=settings.smtp_username,
        password=settings.smtp_password,
        starttls=settings.smtp_starttls,
    )


EmailSenderDep = Annotated[EmailSender, Depends(get_email_sender)]


def get_email_verification_issuer(
    verifications: EmailVerificationRepositoryDep, settings: SettingsDep
) -> EmailVerificationIssuer:
    return EmailVerificationIssuer(
        verifications,
        settings.web_public_url,
        timedelta(hours=settings.email_verification_ttl_hours),
    )


EmailVerificationIssuerDep = Annotated[
    EmailVerificationIssuer, Depends(get_email_verification_issuer)
]


def get_email_quota(session: SessionDep, settings: SettingsDep) -> EmailQuota:
    return EmailQuota(
        SqlAlchemyEmailQuotaRepository(session),
        settings.email_monthly_limit,
        settings.email_quota_reset_day,
    )


EmailQuotaDep = Annotated[EmailQuota, Depends(get_email_quota)]


def get_register_user(
    users: UserRepositoryDep,
    hasher: PasswordHasherDep,
    verification: EmailVerificationIssuerDep,
    quota: EmailQuotaDep,
) -> RegisterUser:
    return RegisterUser(users, hasher, verification, quota)


def get_resend_email_verification(
    users: UserRepositoryDep,
    verifications: EmailVerificationRepositoryDep,
    issuer: EmailVerificationIssuerDep,
    quota: EmailQuotaDep,
) -> ResendEmailVerification:
    return ResendEmailVerification(users, verifications, issuer, quota)


def get_password_reset_repository(session: SessionDep) -> SqlAlchemyPasswordResetRepository:
    return SqlAlchemyPasswordResetRepository(session)


PasswordResetRepositoryDep = Annotated[
    SqlAlchemyPasswordResetRepository, Depends(get_password_reset_repository)
]


def get_request_password_reset(
    users: UserRepositoryDep,
    resets: PasswordResetRepositoryDep,
    quota: EmailQuotaDep,
    settings: SettingsDep,
) -> RequestPasswordReset:
    issuer = PasswordResetIssuer(
        resets, settings.web_public_url, timedelta(minutes=settings.password_reset_ttl_minutes)
    )
    return RequestPasswordReset(users, resets, issuer, quota)


def get_reset_password(
    users: UserRepositoryDep,
    resets: PasswordResetRepositoryDep,
    hasher: PasswordHasherDep,
    quota: EmailQuotaDep,
) -> ResetPassword:
    return ResetPassword(users, resets, hasher, quota)


def get_verify_email(
    users: UserRepositoryDep,
    verifications: EmailVerificationRepositoryDep,
    tokens: TokenServiceDep,
) -> VerifyEmail:
    return VerifyEmail(users, verifications, tokens)


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


def get_membership_notices(
    memberships: MembershipRepositoryDep,
    communities: CommunityRepositoryDep,
    users: UserRepositoryDep,
    quota: EmailQuotaDep,
    settings: SettingsDep,
) -> MembershipNotices:
    return MembershipNotices(memberships, communities, users, quota, settings.web_public_url)


MembershipNoticesDep = Annotated[MembershipNotices, Depends(get_membership_notices)]


def get_community_notices(
    users: UserRepositoryDep, quota: EmailQuotaDep, settings: SettingsDep
) -> CommunityNotices:
    return CommunityNotices(users, quota, settings.web_public_url)


CommunityNoticesDep = Annotated[CommunityNotices, Depends(get_community_notices)]


def get_community_access(
    communities: CommunityRepositoryDep, memberships: MembershipRepositoryDep
) -> CommunityAccess:
    return CommunityAccess(communities, memberships)


CommunityAccessDep = Annotated[CommunityAccess, Depends(get_community_access)]


def get_media_repository(session: SessionDep) -> SqlAlchemyMediaRepository:
    return SqlAlchemyMediaRepository(session)


@lru_cache
def _object_storage(
    endpoint: str,
    public_endpoint: str,
    bucket: str,
    access_key: str,
    secret_key: str,
    region: str,
    addressing_style: str,
) -> S3ObjectStorage:
    # Los clientes de boto3 son costosos de crear y seguros entre hilos: uno por configuración.
    return S3ObjectStorage(
        endpoint, public_endpoint, bucket, access_key, secret_key, region, addressing_style
    )


def get_object_storage(settings: SettingsDep) -> S3ObjectStorage:
    return _object_storage(
        settings.storage_endpoint,
        settings.storage_public_endpoint,
        settings.storage_bucket,
        settings.storage_access_key,
        settings.storage_secret_key,
        settings.storage_region,
        settings.storage_addressing_style,
    )


MediaRepositoryDep = Annotated[SqlAlchemyMediaRepository, Depends(get_media_repository)]
ObjectStorageDep = Annotated[S3ObjectStorage, Depends(get_object_storage)]


def get_category_repository(session: SessionDep) -> SqlAlchemyCategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_listing_repository(session: SessionDep) -> SqlAlchemyListingRepository:
    return SqlAlchemyListingRepository(session)


CategoryRepositoryDep = Annotated[SqlAlchemyCategoryRepository, Depends(get_category_repository)]
ListingRepositoryDep = Annotated[SqlAlchemyListingRepository, Depends(get_listing_repository)]
