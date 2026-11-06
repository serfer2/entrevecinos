## ADDED Requirements

### Requirement: Límite de correos por periodo
La API SHALL enviar como mucho `EMAIL_MONTHLY_LIMIT` correos (5.000 en producción) por periodo, que empieza el día `EMAIL_QUOTA_RESET_DAY` (6) a las 00:00 en hora de `Europe/Madrid` y termina el mismo día del mes siguiente. El contador MUST guardarse en PostgreSQL y la reserva de cada plaza MUST ser atómica. Es una restricción de costes y MUST constar como tal en `infra/aws/README.md`.

#### Scenario: Última plaza
- **WHEN** se han enviado 4.999 correos en el periodo y alguien se registra
- **THEN** se envía su correo y el contador queda en 5.000

#### Scenario: Periodo del 6 al 6
- **WHEN** el límite se alcanzó el 20 de marzo y llega el 6 de abril a las 00:00 (hora de Madrid)
- **THEN** los envíos vuelven a funcionar con el contador del periodo nuevo; del 1 al 5 de abril siguen bloqueados

#### Scenario: Peticiones simultáneas
- **WHEN** quedan una plaza y llegan dos registros a la vez
- **THEN** solo uno la obtiene

### Requirement: Bloqueo al alcanzar el límite
Sin cupo, `POST /auth/register` y `POST /auth/email-verification/resend` SHALL responder `503` con `{"detail": "...", "code": "email_quota_exceeded"}` y `Retry-After` en segundos hasta el siguiente periodo, sin crear la cuenta ni el enlace ni enviar nada. El reenvío MUST comprobar el cupo antes de buscar la cuenta, para responder igual exista o no. La web MUST mostrar «Ahora mismo no podemos enviar correos de validación. Inténtalo de nuevo en unos días.» sin perder los datos del formulario.

#### Scenario: Registro sin cupo
- **WHEN** se han enviado 5.000 correos en el periodo y alguien se registra
- **THEN** recibe `503` con `email_quota_exceeded` y `Retry-After`, y no se crea la cuenta

#### Scenario: Reenvío sin cupo para un correo desconocido
- **WHEN** no queda cupo y se pide el reenvío para un correo que no existe
- **THEN** la respuesta es el mismo `503` que para una cuenta pendiente

### Requirement: Avisos del cupo
La API SHALL registrar un aviso al alcanzar el 80 % del límite (una vez por periodo) y un error en cada envío bloqueado, sin direcciones de correo, y producción MUST avisar por correo de ambos con las alarmas `entrevecinos-prod-email-quota-80` y `entrevecinos-prod-email-quota-exceeded`.

#### Scenario: Aviso del 80 %
- **WHEN** se reserva la plaza 4.000 del periodo
- **THEN** se registra «Cupo de correo al 80 %» y salta la alarma del 80 %
