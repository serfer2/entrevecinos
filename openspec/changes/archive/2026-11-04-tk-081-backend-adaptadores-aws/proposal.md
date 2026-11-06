## Why

HU-36: en AWS la API debe usar S3 y SES con las credenciales temporales del rol de la instancia, sin claves de acceso de larga duración (HU-36 AC4). Hoy `S3ObjectStorage` exige claves, endpoint y la región `us-east-1`, y el correo solo sale por SMTP. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-081-backend-adaptadores-aws.md`.

## What Changes

- `Settings`: endpoints y claves de almacenamiento opcionales (las dos claves o ninguna), `STORAGE_REGION`, `STORAGE_ADDRESSING_STYLE` (`path` | `virtual`), `MAIL_BACKEND` (`smtp` | `ses`), `SES_REGION` y `SES_CONFIGURATION_SET`; `SMTP_HOST` solo obligatorio con `smtp` y STARTTLS solo exigido en producción con `smtp`. Mensajes de error en español.
- `S3ObjectStorage`: sin claves usa la cadena de credenciales por defecto de boto3; sin endpoint, el de la región; firma con la región y el estilo configurados.
- `SesEmailSender` (nuevo): `sesv2.send_email` con texto y HTML y *configuration set* opcional; la composición elige el adaptador según `MAIL_BACKEND`.
- `.env.example`, `infra/docker-compose.yml` (`MAIL_BACKEND`) y `apps/api/README.md`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `email-delivery`: configuración con `MAIL_BACKEND` y envío por la API de SES.
- `object-storage`: almacenamiento en S3 de AWS con las credenciales del rol y la región.

## Impact

- `apps/api/src/entrevecinos/infrastructure/` (`settings.py`, `storage/s3_object_storage.py`, `mail/ses_email_sender.py`), `presentation/dependencies.py`, `apps/api/tests/test_aws_adapters.py`.
- Sin cambios de contrato de la API ni migraciones. Sin dependencias nuevas (`boto3` ya está).
