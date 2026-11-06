import ssl
from unittest.mock import MagicMock, patch

from entrevecinos.application.users.ports import OutgoingEmail
from entrevecinos.infrastructure.mail.smtp_email_sender import SmtpEmailSender

EMAIL = OutgoingEmail(
    to="vecino@example.com", subject="Valida tu correo", text="texto", html="<p>h</p>"
)


def send_with(sender: SmtpEmailSender) -> MagicMock:
    with patch("entrevecinos.infrastructure.mail.smtp_email_sender.smtplib.SMTP") as smtp_class:
        sender.send(EMAIL)
    return smtp_class.return_value.__enter__.return_value


def test_starttls_verifies_the_server_certificate() -> None:
    smtp = send_with(
        SmtpEmailSender(
            "smtp-relay.brevo.com", 587, "no-reply@entrevecinos.org", username="u", password="p"
        )
    )

    context = smtp.starttls.call_args.kwargs["context"]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    smtp.login.assert_called_once_with("u", "p")
    smtp.send_message.assert_called_once()


def test_without_starttls_or_credentials_sends_in_plain_text() -> None:
    smtp = send_with(SmtpEmailSender("mail", 1025, "no-reply@entrevecinos.local", starttls=False))

    smtp.starttls.assert_not_called()
    smtp.login.assert_not_called()
    smtp.send_message.assert_called_once()
