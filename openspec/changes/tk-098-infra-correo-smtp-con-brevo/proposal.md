## Why

HU-40: TK-096 eligió Brevo porque SES no sale del *sandbox*. Falta llevar el correo de producción a Brevo: autenticar el dominio, pasar las credenciales a la API, permitir la salida SMTP desde una IP fija autorizada en Brevo y cambiar la configuración. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-40-recibir-el-correo-de-validacion-en-cualquier-direccion/TK-098-infra-correo-smtp-con-brevo.md`.

## What Changes

- DNS en Route 53 (Terraform):
  - TXT `brevo-code` en el mismo conjunto que el SPF de la raíz (`root_txt_records` en `modules/domain`);
  - DMARC con `rua` de Brevo, conservando `adkim` y `aspf` (`dmarc_rua`);
  - cinco CNAME de Brevo (`modules/mail/brevo.tf`): DKIM y marca con el prefijo `send`.
- `modules/compute`:
  - IP elástica asociada a la instancia, con `prevent_destroy`;
  - el origen de CloudFront usa su nombre DNS;
  - salida `instance_public_ip`.
- `modules/network`: salida TCP 587.
- `infra/docker-compose.prod.yml`: `MAIL_BACKEND=smtp` hacia `smtp-relay.brevo.com:587` con STARTTLS; `SMTP_USERNAME` y `SMTP_PASSWORD` desde `deploy.sh`; sin `SES_*`.
- `infra/prod/deploy.sh`: lee `/entrevecinos/prod/smtp/{username,password}` en la misma llamada y los pasa solo por entorno.
- `apps/api`: `SmtpEmailSender` verifica el certificado y el nombre del servidor en STARTTLS. Sin contexto, `smtplib` no lo hace y un intermediario podría robar las credenciales.
- `infra/aws/README.md`: estructura, DNS, secretos, instancia (IP fija y salida), *runbook* de correo y destrucción.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `email-provider`: integración con Brevo (DNS, IP fija autorizada, salida SMTP y configuración de producción).
- `email-delivery`: STARTTLS con verificación del certificado del servidor.

## Impact

- Infraestructura: `infra/aws/modules/{domain,mail,compute,network}`, `infra/aws/envs/prod`, `infra/docker-compose.prod.yml`, `infra/prod/deploy.sh`; `infra/aws/README.md` («Estructura», «DNS», «Secretos», «Operación», «Destruir el entorno»).
- API: `infrastructure/mail/smtp_email_sender.py` y su prueba; sin cambios de contrato ni migraciones.
- Exige `make tf-apply`; tras él, autorizar la IP elástica en Brevo, verificar el dominio y desactivar el seguimiento de clics; después, desplegar.
