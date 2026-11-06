## Why

HU-40 AC2 y AC3: con el correo de producción por Brevo (TK-098), sobran los destinatarios de prueba de SES y su permiso de envío. Además, un correo que no sale pasa desapercibido: el registro responde `201` y el envío va después, en segundo plano, y la alarma `api-errors` necesita más de 10 errores. Así nadie notó que el *sandbox* bloqueaba los registros. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-40-recibir-el-correo-de-validacion-en-cualquier-direccion/TK-097-infra-correo-de-produccion-sin-sandbox.md`.

## What Changes

- `ses_test_recipients = []` en `prod.tfvars` (local, fuera del repositorio). Terraform borra la identidad de prueba de SES y el permiso `ses:SendEmail` del rol queda limitado al dominio y al *configuration set*. La variable se mantiene por si hay que volver a SES en *sandbox*.
- Alarma `entrevecinos-prod-email-send-failures`: filtro sobre «No se pudo enviar el correo» en `/entrevecinos/prod/app/api` (métrica `EmailSendFailures`); salta con el primer fallo en 5 minutos, con aviso al volver a `OK`. Nueva línea en el panel.
- `infra/aws/README.md`: «Puesta en marcha» sin destinatarios de prueba, límites reales del correo, *runbook* de la alarma y costes.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `observability`: alarma del primer fallo de envío de correo.
- `aws-mail-secrets`: los destinatarios de prueba solo existen si se vuelve a SES en *sandbox*; en producción, ninguno.

## Impact

- Infraestructura: `infra/aws/modules/observability/` y `prod.tfvars` (local); `infra/aws/README.md` («Puesta en marcha», «Observabilidad y alertas», «Costes»). Exige `make tf-apply`. Sin cambios de la API, del contrato ni migraciones.
