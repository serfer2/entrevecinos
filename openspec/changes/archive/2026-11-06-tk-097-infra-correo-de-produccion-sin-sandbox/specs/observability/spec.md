## ADDED Requirements

### Requirement: Aviso del primer fallo de envío de correo
Producción SHALL tener la alarma `entrevecinos-prod-email-send-failures`, sobre la métrica `EmailSendFailures` que cuenta el mensaje «No se pudo enviar el correo» del registro de la API, y MUST avisar al tema `entrevecinos-prod-alerts` con el primer fallo en 5 minutos y al volver a `OK`, tratando los datos ausentes como correctos.

#### Scenario: Correo rechazado por el proveedor
- **WHEN** el servidor SMTP rechaza un correo de la aplicación
- **THEN** salta la alarma y llega un aviso por correo

#### Scenario: Rebote posterior
- **WHEN** el proveedor acepta el correo y después rebota (dirección inexistente)
- **THEN** la alarma no salta: el rebote queda en los registros del proveedor
