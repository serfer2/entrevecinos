## Why

HU-36: la API envía el enlace de validación por SES y necesita `JWT_SECRET` sin que esté en el repositorio (HU-36 AC4). Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-083-infra-correo-ses-y-secretos.md`.

## What Changes

- `modules/mail`: *configuration set* `entrevecinos-prod` (TLS obligatorio, métricas de reputación, supresión de rebotes y quejas) con eventos de envío en CloudWatch; supresión a nivel de cuenta; destinatarios de prueba opcionales para el *sandbox*.
- `/entrevecinos/prod/jwt-secret` en Parameter Store (`SecureString`), generado con `ephemeral "random_password"` y escrito con `value_wo`: no queda en el estado.
- Procedimiento de salida del *sandbox* en `infra/aws/README.md`.

## Capabilities

### New Capabilities
- `aws-mail-secrets`: configuración de SES para el envío y secretos de la aplicación en Parameter Store.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/mail/`, `infra/aws/envs/prod/` («Puesta en marcha» y «Secretos» de `infra/aws/README.md`).
- Crea recursos en AWS (coste 0). La identidad del dominio llega en TK-084.
