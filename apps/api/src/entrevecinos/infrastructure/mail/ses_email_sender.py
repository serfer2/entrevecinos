from typing import Any

import boto3

from entrevecinos.application.users.ports import OutgoingEmail


class SesEmailSender:
    """Envía el correo con la API de Amazon SES v2 (producción, TK-081).

    Usa las credenciales temporales del rol de la instancia: no hay contraseña SMTP de larga
    duración. Los errores de SES (`ClientError`) se propagan como los de SMTP.
    """

    def __init__(
        self, sender: str, region: str, *, configuration_set: str = "", client: Any = None
    ) -> None:
        self._sender = sender
        self._configuration_set = configuration_set
        self._client = client or boto3.client("sesv2", region_name=region)

    def send(self, email: OutgoingEmail) -> None:
        request: dict[str, Any] = {
            "FromEmailAddress": self._sender,
            "Destination": {"ToAddresses": [email.to]},
            "Content": {
                "Simple": {
                    "Subject": {"Data": email.subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": email.text, "Charset": "UTF-8"},
                        "Html": {"Data": email.html, "Charset": "UTF-8"},
                    },
                }
            },
        }
        if self._configuration_set:
            request["ConfigurationSetName"] = self._configuration_set
        self._client.send_email(**request)
