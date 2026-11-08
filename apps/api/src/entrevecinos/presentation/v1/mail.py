import logging

from entrevecinos.application.users.ports import EmailSender, OutgoingEmail

logger = logging.getLogger(__name__)


def send_in_background(sender: EmailSender, email: OutgoingEmail) -> None:
    """Se ejecuta tras responder: si el envío falla, la operación ya está hecha y se anota el error.

    La alarma `email-send-failures` busca este mensaje en el registro de la API (TK-097).
    """
    try:
        sender.send(email)
    except Exception:
        logger.exception("No se pudo enviar el correo «%s»", email.subject)
