## Why

HU-36 y HU-38: para ahorrar costes mientras el proyecto no escale, PostgreSQL corre en la instancia en lugar de RDS. Eso exige un volumen de datos que sobreviva a la instancia, copias frecuentes comprobables que la instancia no pueda borrar y roles de mínimo privilegio. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-082-infra-base-de-datos-en-la-instancia.md`.

## What Changes

- `modules/database`: volumen EBS `gp3` cifrado (10 GB, `prevent_destroy`), *snapshots* diarios con Data Lifecycle Manager (7), bucket de copias (30 días) cuya política deniega el borrado salvo a los roles de administración, y contraseñas de `postgres`, `entrevecinos_owner` y `entrevecinos_app` en Parameter Store (`ephemeral` + `value_wo`), con los parámetros de conexión.
- `infra/prod/initdb/10-roles.sh`: roles idempotentes; la API solo tiene DML.
- `infra/prod/backup.sh` y temporizador `systemd` cada 6 horas: `pg_dump` en *streaming* a S3, comprobación con `pg_restore --list` y métrica `BackupSucceeded`.
- Decisión de arquitectura en `infra/aws/README.md`.

## Capabilities

### New Capabilities
- `production-database`: PostgreSQL de producción en la instancia, con volumen, roles, copias y su decisión documentada.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/database/`, `infra/aws/envs/prod/`, `infra/prod/` («Secretos», «Operación» y «Decisiones de arquitectura» de `infra/aws/README.md`).
- Crea recursos en AWS (≈ 1 USD/mes: volumen y *snapshots*). El contenedor `db` y la instalación de los *scripts* llegan en TK-086; el adjunto del volumen, en TK-085.
