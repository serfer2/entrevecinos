# production-database Specification

## Purpose
PostgreSQL de producción en la propia instancia mientras el proyecto no escale: volumen EBS cifrado con snapshots, roles separados para migraciones y aplicación, contraseñas en Parameter Store fuera del estado de Terraform y copias comprobadas cada 6 horas en un bucket protegido contra borrado.
## Requirements
### Requirement: Volumen de datos de PostgreSQL
Terraform SHALL crear un volumen EBS `gp3` cifrado para los datos de PostgreSQL, en la zona de la subred de la instancia, protegido contra borrado y separado del volumen raíz, con *snapshots* diarios que se conservan 7 días.

#### Scenario: Snapshots
- **WHEN** consulto las políticas de Data Lifecycle Manager
- **THEN** hay una política activa que hace un *snapshot* diario del volumen y conserva 7

### Requirement: Roles de mínimo privilegio
`infra/prod/initdb/10-roles.sh` SHALL crear de forma idempotente `entrevecinos_owner` (propietario de la base y del esquema, para las migraciones) y `entrevecinos_app` (para la API), con las contraseñas recibidas por entorno; `entrevecinos_app` MUST poder hacer `SELECT`, `INSERT`, `UPDATE` y `DELETE` en las tablas de la aplicación y MUST NOT poder crear, modificar, vaciar ni borrar tablas.

#### Scenario: DDL denegado
- **WHEN** `entrevecinos_app` ejecuta `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE` o `TRUNCATE`
- **THEN** PostgreSQL lo deniega

#### Scenario: Migraciones como propietario
- **WHEN** se ejecuta `alembic upgrade head` como `entrevecinos_owner` sobre una base recién creada
- **THEN** se aplican todas las migraciones, incluida la extensión `unaccent`

#### Scenario: Rotación
- **WHEN** se vuelve a ejecutar el *script* con contraseñas nuevas
- **THEN** las nuevas funcionan y las anteriores se rechazan

### Requirement: Copias cada 6 horas comprobadas
`infra/prod/backup.sh`, ejecutado cada 6 horas por `entrevecinos-backup.timer`, SHALL subir un `pg_dump` en formato personalizado al bucket de copias con SSE-S3, sin dejarlo en disco, y MUST considerarlo fallido si ocupa menos del mínimo o `pg_restore --list` no lo lee; si es correcto, MUST publicar `Entrevecinos/Backup BackupSucceeded = 1`.

#### Scenario: Copia correcta
- **WHEN** se ejecuta `backup.sh`
- **THEN** hay una copia nueva en `postgres/AAAA/MM/DD/` y se publica la métrica

### Requirement: Copias que la instancia no puede borrar
El bucket de copias SHALL conservar las copias 30 días y su política MUST denegar `s3:DeleteObject` y `s3:DeleteObjectVersion` a cualquier principal que no esté en `admin_role_arns`.

#### Scenario: Borrado desde la instancia
- **WHEN** el rol de la instancia intenta borrar una copia
- **THEN** se deniega

### Requirement: Contraseñas fuera del repositorio y del estado
Las contraseñas de los tres roles SHALL guardarse como `SecureString` en `/entrevecinos/prod/db/`, generadas con recursos efímeros y escritas con argumentos de solo escritura, y MUST NOT aparecer en el repositorio ni en el estado.

#### Scenario: Parámetros
- **WHEN** listo `/entrevecinos/prod/db/`
- **THEN** hay tres contraseñas `SecureString` y los parámetros `host`, `port` y `name`

### Requirement: Decisión documentada
`infra/aws/README.md` SHALL documentar que la base de datos corre en la instancia para ahorrar costes mientras el proyecto no escale, con su impacto, sus mitigaciones, cuándo revisarla y cómo migrar a RDS.

#### Scenario: Decisión
- **WHEN** leo «Decisiones de arquitectura»
- **THEN** encuentro la entrada «Base de datos en la instancia (TK-082)»

