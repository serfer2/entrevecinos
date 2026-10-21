import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status

from entrevecinos.application.users.authenticate_user import AuthenticateUser, LoginCommand
from entrevecinos.application.users.ports import EmailSender, OutgoingEmail
from entrevecinos.application.users.register_user import RegisterUser, RegisterUserCommand
from entrevecinos.application.users.resend_email_verification import ResendEmailVerification
from entrevecinos.application.users.verify_email import VerifyEmail
from entrevecinos.presentation.dependencies import (
    EmailSenderDep,
    get_authenticate_user,
    get_register_user,
    get_resend_email_verification,
    get_verify_email,
)
from entrevecinos.presentation.v1.schemas.auth import (
    AuthResponse,
    EmailNotVerifiedResponse,
    EmailVerificationRequest,
    LoginRequest,
    RegisterRequest,
    RegistrationConflictResponse,
    RegistrationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerificationErrorResponse,
)
from entrevecinos.presentation.v1.schemas.common import UNAUTHORIZED, VALIDATION_ERROR
from entrevecinos.presentation.v1.schemas.users import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def send_in_background(sender: EmailSender, email: OutgoingEmail) -> None:
    """Se ejecuta tras responder: si el SMTP falla, la cuenta sigue creada y se anota el error."""
    try:
        sender.send(email)
    except Exception:
        logger.exception("No se pudo enviar el correo «%s»", email.subject)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    operation_id="registerUser",
    summary="Registrar una cuenta",
    description=(
        "Crea una cuenta inactiva con rol `user` y envía un correo con el enlace de validación. "
        "La cuenta se activa al validar el correo (`POST /auth/email-verification`)."
    ),
    responses={409: {"model": RegistrationConflictResponse}, **VALIDATION_ERROR},
)
def register(
    body: RegisterRequest,
    register_user: Annotated[RegisterUser, Depends(get_register_user)],
    sender: EmailSenderDep,
    background_tasks: BackgroundTasks,
) -> RegistrationResponse:
    registration = register_user.execute(
        RegisterUserCommand(
            email=body.email, password=body.password, full_name=body.full_name, phone=body.phone
        )
    )
    background_tasks.add_task(send_in_background, sender, registration.verification_email)
    return RegistrationResponse(
        email=registration.user.email,
        verification_expires_at=registration.verification_expires_at,
    )


@router.post(
    "/email-verification",
    operation_id="verifyEmail",
    summary="Validar el correo electrónico",
    description=(
        "Valida el correo con el token del enlace, activa la cuenta y emite un token JWT. "
        "Acceso público."
    ),
    responses={
        400: {"model": VerificationErrorResponse},
        410: {"model": VerificationErrorResponse},
        **VALIDATION_ERROR,
    },
)
def verify_email(
    body: EmailVerificationRequest,
    verify: Annotated[VerifyEmail, Depends(get_verify_email)],
) -> AuthResponse:
    user, token = verify.execute(body.token)
    return AuthResponse(
        access_token=token.token, expires_in=token.expires_in, user=UserResponse.from_domain(user)
    )


@router.post(
    "/email-verification/resend",
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="resendEmailVerification",
    summary="Reenviar el correo de validación",
    description=(
        "Envía un enlace de validación nuevo si la cuenta está pendiente. Responde lo mismo exista "
        "o no la cuenta, para no revelar qué correos están registrados. Acceso público."
    ),
    responses={**VALIDATION_ERROR},
)
def resend_email_verification(
    body: ResendVerificationRequest,
    resend: Annotated[ResendEmailVerification, Depends(get_resend_email_verification)],
    sender: EmailSenderDep,
    background_tasks: BackgroundTasks,
) -> ResendVerificationResponse:
    message = resend.execute(body.email)
    if message is not None:
        background_tasks.add_task(send_in_background, sender, message)
    return ResendVerificationResponse(
        detail="Si el correo está pendiente de validación, te enviaremos un enlace nuevo."
    )


@router.post(
    "/token",
    operation_id="loginUser",
    summary="Iniciar sesión",
    description="Valida las credenciales y emite un token JWT. Acceso público.",
    responses={**UNAUTHORIZED, 403: {"model": EmailNotVerifiedResponse}, **VALIDATION_ERROR},
)
def login(
    body: LoginRequest,
    authenticate_user: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
) -> AuthResponse:
    user, token = authenticate_user.execute(LoginCommand(email=body.email, password=body.password))
    return AuthResponse(
        access_token=token.token, expires_in=token.expires_in, user=UserResponse.from_domain(user)
    )
