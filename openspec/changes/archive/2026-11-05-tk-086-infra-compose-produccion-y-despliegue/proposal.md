## Why

HU-36: la instancia endurecida (TK-085) ya existe, pero no ejecuta nada. Falta un Compose de producción seguro y un despliegue reproducible, con migraciones, comprobación de salud y vuelta atrás, que no deje secretos en disco (HU-36 AC2 a AC4). Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-086-infra-compose-produccion-y-despliegue.md`.

## What Changes

- `infra/docker-compose.prod.yml` (nuevo): `proxy` (nginx sin *root*), `web`, `api` y `db` (PostgreSQL 16) con imágenes por *digest*, redes separadas (la web no llega a la base de datos), contenedores endurecidos (solo lectura, sin capacidades, `no-new-privileges`, límites), *healthchecks*, logs en CloudWatch y secretos solo por entorno (`${VAR:?}`, sin `env_file`).
- `infra/prod/proxy/default.conf.template` (nuevo): `403` a toda petición sin la cabecera `X-Origin-Verify` correcta; el resto, a `web:3000` sin esa cabecera.
- `infra/prod/deploy.sh` (nuevo): ECR, secretos de Parameter Store al entorno del proceso, roles de PostgreSQL, migraciones como `entrevecinos_owner`, arranque, salud, vuelta atrás a los *digests* anteriores, instalación del temporizador de copias y limpieza de imágenes.
- `infra/prod/backup.sh` y su unidad: localizan el contenedor `db` con `docker` (no con `docker compose`, que exigiría los secretos) y viven en `/opt/entrevecinos/prod/`.
- Terraform (`modules/compute`): documento de SSM `entrevecinos-deploy` que copia `infra/prod/` y el Compose a la instancia y ejecuta `deploy.sh`; grupos de logs de los contenedores y del despliegue; parámetro `/entrevecinos/prod/origin-verify`.
- Primer despliegue manual con imágenes `arm64` subidas desde el equipo.

## Capabilities

### New Capabilities
- `production-deployment`: Compose de producción, proxy de origen, despliegue con migraciones, salud y vuelta atrás, y secretos solo por entorno.

### Modified Capabilities
- `production-database`: las copias se instalan en cada despliegue y se ejecutan sobre el contenedor `db` sin depender de los secretos del Compose.

## Impact

- Rutas de infraestructura: `infra/docker-compose.prod.yml`, `infra/prod/` y `infra/aws/modules/compute/` (`infra/aws/README.md`: «Puesta en marcha», «Despliegue», «Secretos», «Operación», «Costes» y «Decisiones de arquitectura»).
- Sin cambios de contrato de la API ni migraciones nuevas; las existentes se aplican por primera vez en producción.
- Coste: logs de CloudWatch de los contenedores (dentro de los 5 GB gratuitos al mes con tráfico de MVP).
