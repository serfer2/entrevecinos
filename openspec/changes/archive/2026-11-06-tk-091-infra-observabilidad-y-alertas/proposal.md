## Why

HU-38 AC1 y AC2: producción ya envía registros a CloudWatch, pero sin retención homogénea, sin métricas de memoria ni disco y sin avisos. Con una sola instancia sin alta disponibilidad, cualquier fallo deja la web sin servicio y hay que enterarse antes que los vecinos. Además, los registros del proxy y de CloudFront guardan la cadena de consulta, donde viaja el *token* de validación del correo (`/verificar-correo?token=…`). Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-38-vigilar-recuperar-y-operar-produccion/TK-091-infra-observabilidad-y-alertas.md`.

## What Changes

- Nuevo módulo `infra/aws/modules/observability/`:
  - tema SNS `entrevecinos-prod-alerts` con suscripción por correo a `alert_email` (solo `eu-north-1`: la política de control de servicios deniega SNS en `us-east-1`);
  - configuración del agente de CloudWatch en Parameter Store (`mem_used_percent`, `swap_used_percent`, `disk_used_percent` de `/` y del volumen de datos, y el registro de las copias) aplicada con una asociación de State Manager (`AmazonCloudWatch-ManageAgent`);
  - filtros de métricas: errores de PostgreSQL (`FATAL`/`PANIC`), errores de la API, peticiones y `5xx` del proxy y rechazos `429`;
  - 12 alarmas con aviso al entrar en `ALARM` y al volver a `OK`: instancia caída, CPU, créditos de CPU, memoria, disco raíz, disco de datos, copia ausente, errores de PostgreSQL, errores de la API, tasa de `5xx` de la web (registro del proxy), rebotes y quejas de SES;
  - panel `entrevecinos-prod`.
- `modules/compute`: grupo `/entrevecinos/prod/app/backup` y retención de 14 días en los de los contenedores y las copias (el de despliegues sigue en 30).
- `infra/prod/systemd/entrevecinos-backup.service`: la salida va a `/var/log/entrevecinos/backup.log`, que el agente envía a CloudWatch.
- Registros sin datos sensibles: el proxy registra la ruta sin la cadena de consulta y CloudFront solo los campos elegidos, sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)`.
- `infra/aws/README.md`: «Observabilidad y alertas», *runbook* de cada alarma, costes y decisiones.

## Capabilities

### New Capabilities
- `observability`: retención de registros, métricas del agente, alarmas con aviso por correo y panel de producción.

### Modified Capabilities
- `aws-edge`: los registros de acceso de CloudFront excluyen la cadena de consulta, las *cookies* y el *referer*.
- `production-deployment`: retención de 14 días en los registros de los contenedores, grupo de las copias y proxy sin cadena de consulta en su registro.

## Impact

- Infraestructura: nuevo `infra/aws/modules/observability/`; cambios en `infra/aws/modules/compute/` (grupos de registros), `infra/aws/modules/edge/logs.tf` (campos), `infra/aws/envs/prod/` (módulo y salidas), `infra/prod/proxy/default.conf.template` y `infra/prod/systemd/entrevecinos-backup.service`.
- `infra/aws/README.md`: «Estructura», «Operación», «Observabilidad y alertas» (nueva), «Costes» y «Decisiones de arquitectura».
- Exige `make tf-apply` antes del siguiente despliegue (el documento de SSM incrusta `infra/prod/`) y confirmar la suscripción de SNS por correo.
- Sin cambios de la API, del contrato ni migraciones.
