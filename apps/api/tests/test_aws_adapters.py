"""Adaptadores para AWS (TK-081): credenciales del rol, región y SES."""

from urllib.parse import parse_qs, urlparse

import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from pydantic import ValidationError

from entrevecinos.application.users.ports import OutgoingEmail
from entrevecinos.infrastructure.mail.ses_email_sender import SesEmailSender
from entrevecinos.infrastructure.mail.smtp_email_sender import SmtpEmailSender
from entrevecinos.infrastructure.storage.s3_object_storage import S3ObjectStorage
from entrevecinos.presentation.dependencies import get_email_sender
from tests.conftest import make_settings

EMAIL = OutgoingEmail(
    to="vecina@example.com", subject="Valida tu correo", text="Hola", html="<p>Hola</p>"
)


# --- Settings ---


def test_aws_settings_without_storage_keys_or_smtp() -> None:
    settings = make_settings(
        environment="production",
        web_public_url="https://entrevecinos.org",
        storage_endpoint="",
        storage_public_endpoint="",
        storage_access_key="",
        storage_secret_key="",
        storage_region="eu-north-1",
        storage_addressing_style="virtual",
        mail_backend="ses",
        smtp_host="",
        smtp_starttls=False,
    )

    assert settings.mail_backend == "ses"
    assert settings.storage_access_key == ""


@pytest.mark.parametrize(
    "overrides",
    [{"storage_access_key": ""}, {"storage_secret_key": ""}],
)
def test_storage_keys_must_come_together(overrides: dict) -> None:
    with pytest.raises(ValidationError, match="STORAGE_ACCESS_KEY y STORAGE_SECRET_KEY"):
        make_settings(**overrides)


def test_unknown_mail_backend_fails() -> None:
    with pytest.raises(ValidationError, match="MAIL_BACKEND debe ser"):
        make_settings(mail_backend="sendgrid")


def test_unknown_addressing_style_fails() -> None:
    with pytest.raises(ValidationError, match="STORAGE_ADDRESSING_STYLE debe ser"):
        make_settings(storage_addressing_style="dns")


def test_smtp_backend_requires_host() -> None:
    with pytest.raises(ValidationError, match="SMTP_HOST"):
        make_settings(mail_backend="smtp", smtp_host="")


# --- S3ObjectStorage ---


def test_storage_without_keys_uses_default_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    # En AWS las credenciales llegan del rol de la instancia; aquí, de la cadena por defecto.
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "ASIAROLECREDENTIALS")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "role-secret")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "role-session-token")
    storage = S3ObjectStorage(
        "", "", "entrevecinos-media", region="eu-north-1", addressing_style="virtual"
    )

    url = urlparse(storage.presigned_get_url("listings/x.png", 300))
    query = parse_qs(url.query)

    assert url.scheme == "https"
    assert url.netloc == "entrevecinos-media.s3.eu-north-1.amazonaws.com"
    assert url.path == "/listings/x.png"
    assert query["X-Amz-Credential"][0].startswith("ASIAROLECREDENTIALS/")
    assert "/eu-north-1/s3/" in query["X-Amz-Credential"][0]
    assert query["X-Amz-Security-Token"] == ["role-session-token"]


def test_storage_with_keys_ignores_default_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "ASIAROLECREDENTIALS")
    storage = S3ObjectStorage("http://storage:9000", "http://localhost:9000", "b", "k", "s")

    url = storage.presigned_get_url("media/x.png", 300)

    assert url.startswith("http://localhost:9000/b/media/x.png")
    assert "X-Amz-Credential=k%2F" in url


# --- SesEmailSender ---


def _ses_client():
    return boto3.client(
        "sesv2",
        region_name="eu-north-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def _expected_request(**extra: str) -> dict:
    return {
        "FromEmailAddress": "EntreVecinos <no-reply@entrevecinos.org>",
        "Destination": {"ToAddresses": ["vecina@example.com"]},
        "Content": {
            "Simple": {
                "Subject": {"Data": "Valida tu correo", "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": "Hola", "Charset": "UTF-8"},
                    "Html": {"Data": "<p>Hola</p>", "Charset": "UTF-8"},
                },
            }
        },
        **extra,
    }


def test_ses_sends_with_configuration_set() -> None:
    client = _ses_client()
    sender = SesEmailSender(
        "EntreVecinos <no-reply@entrevecinos.org>",
        "eu-north-1",
        configuration_set="entrevecinos-prod",
        client=client,
    )

    with Stubber(client) as stubber:
        stubber.add_response(
            "send_email",
            {"MessageId": "m-1"},
            _expected_request(ConfigurationSetName="entrevecinos-prod"),
        )
        sender.send(EMAIL)
        stubber.assert_no_pending_responses()


def test_ses_sends_without_configuration_set() -> None:
    client = _ses_client()
    sender = SesEmailSender("EntreVecinos <no-reply@entrevecinos.org>", "eu-north-1", client=client)

    with Stubber(client) as stubber:
        stubber.add_response("send_email", {"MessageId": "m-1"}, _expected_request())
        sender.send(EMAIL)
        stubber.assert_no_pending_responses()


def test_ses_errors_propagate() -> None:
    client = _ses_client()
    sender = SesEmailSender("EntreVecinos <no-reply@entrevecinos.org>", "eu-north-1", client=client)

    with Stubber(client) as stubber:
        stubber.add_client_error("send_email", "MessageRejected", "Email address is not verified.")
        with pytest.raises(ClientError, match="MessageRejected"):
            sender.send(EMAIL)


# --- Composición ---


def test_email_sender_follows_mail_backend() -> None:
    assert isinstance(get_email_sender(make_settings()), SmtpEmailSender)
    assert isinstance(get_email_sender(make_settings(mail_backend="ses")), SesEmailSender)
