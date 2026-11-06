## Why

HU-38 AC3 y AC4: producción hace copias con `pg_dump` cada 6 horas y *snapshots* diarios (TK-082), y las imágenes tienen versionado (TK-080), pero nunca se ha restaurado nada ni hay procedimientos ni objetivos de recuperación. Una copia que no se ha restaurado no garantiza nada. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-38-vigilar-recuperar-y-operar-produccion/TK-092-infra-copias-y-recuperacion.md`.

## What Changes

- `infra/prod/restore.sh` (nuevo), instalado por el despliegue en `/opt/entrevecinos/prod/`:
  - ensayo (`restore.sh [--target entrevecinos_<x>] <clave>`): restaura en una base aparte (por defecto `entrevecinos_restore`) sin tocar producción y muestra los recuentos de `users`, `community`, `listing` y `media_asset`;
  - producción (`--production --yes`): copia previa, restauración en una base nueva, API parada, cambio de nombre de las bases (la anterior se conserva como `entrevecinos_anterior_<fecha>`) y API arrancada;
  - siempre restaura como `entrevecinos_owner` y aplica los permisos de `entrevecinos_app`; solo admite bases `entrevecinos_*`.
- `deploy.sh`: copia previa con `backup.sh` antes de migrar cuando hay migraciones pendientes; si falla, no migra ni despliega.
- `modules/compute`: el documento de SSM incluye `restore.sh`.
- `infra/aws/README.md`: objetivos RPO 6 h y RTO 4 h, procedimientos (error de datos, fallo del volumen, pérdida de la instancia, imagen borrada) y registro de ensayos.
- Ensayos reales: restauración desde `pg_dump`, PostgreSQL sobre un volumen creado desde *snapshot* y recuperación de una imagen borrada.

## Capabilities

### New Capabilities
- `database-recovery`: objetivos de recuperación, restauración desde copia, recuperación desde *snapshot*, recuperación de imágenes y ensayos registrados.

### Modified Capabilities
- `production-deployment`: el despliegue hace una copia antes de aplicar migraciones pendientes.

## Impact

- Infraestructura: nuevo `infra/prod/restore.sh`; cambios en `infra/prod/deploy.sh` e `infra/aws/modules/compute/deploy.tf`.
- `infra/aws/README.md`: «Estructura», «Base de datos y copias», nueva «Recuperación» y «Decisiones de arquitectura».
- Exige `make tf-apply` y un despliegue para instalar `restore.sh`. Sin cambios de la API, del contrato ni migraciones.
