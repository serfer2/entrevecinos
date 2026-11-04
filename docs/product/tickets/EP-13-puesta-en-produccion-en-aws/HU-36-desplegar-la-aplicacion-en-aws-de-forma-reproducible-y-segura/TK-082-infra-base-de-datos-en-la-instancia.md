# TK-082 · Infraestructura: PostgreSQL en la instancia, volumen de datos y copias de seguridad

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / base de datos |
| **Componente** | `infra/aws/modules/database/` (volumen EBS, bucket de copias, *snapshots*, parámetros), `infra/prod/` (`backup.sh`, `initdb/`, unidades `systemd`), `infra/aws/README.md` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-079, TK-080 |
| **Referencias** | `readme.md` §2.4 y §2.5 (copias y retención); TK-001 (PostgreSQL 16 en Compose; «fijar la versión menor en el ticket de producción»); migración `0003_unaccent`; Amazon Data Lifecycle Manager |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El README prevé PostgreSQL gestionado en producción. Para recortar costes **mientras el proyecto no escale** (decisión del proyecto: la alta disponibilidad no es necesaria hasta que sea maduro y tenga mucho tráfico), PostgreSQL 16 se ejecuta como contenedor en la misma instancia EC2 que la web y la API, en lugar de Amazon RDS. Ahorro aproximado: 15 USD/mes, dentro del límite de 40 €/mes de TK-078.

Esta decisión aumenta cuatro riesgos respecto a RDS: pérdida de datos entre copias, copias que fallan sin aviso, pérdida de la instancia con los datos y acceso a la base si se compromete la instancia. El ticket incluye las cuatro mitigaciones acordadas:

1. **Copias cada 6 horas** con `pg_dump` a S3 cifrado, más *snapshots* diarios del volumen.
2. **Alarma si falta una copia** (TK-091).
3. **Volumen EBS de datos separado** de la raíz, que sobrevive a la instancia.
4. **Usuario de aplicación sin privilegios de administración.**

**Objetivo:** que PostgreSQL funcione en la instancia con los datos en un volumen propio, copias automáticas comprobables y roles de mínimo privilegio, y que la decisión y el camino de vuelta a RDS queden documentados.

## 2. Alcance

**Incluye**
- **Volumen de datos** `aws_ebs_volume` `gp3` de 10 GB (asumido), cifrado, en la misma zona de disponibilidad que la instancia, con `prevent_destroy`. Se adjunta a la instancia en TK-085 (`aws_volume_attachment`) y se monta en `/srv/entrevecinos/postgres` (por UUID en `/etc/fstab`, `nofail`). Terminar o reemplazar la instancia no borra el volumen.
- **Snapshots diarios del volumen** con Data Lifecycle Manager: una vez al día, conservar 7 (asumido), etiquetados.
- **Bucket de copias** `entrevecinos-backups-995006761619`: Block Public Access, SSE-S3, TLS obligatorio, versionado, caducidad de objetos a los 30 días y de versiones no actuales a los 7 (asumido). Política de bucket que **deniega el borrado** (`s3:DeleteObject*`) a todos salvo a los administradores del proyecto: la instancia solo puede escribir (TK-085), así que quien la comprometa no puede borrar las copias.
- **Contenedor `db`** (definido en el Compose de producción de TK-086): `postgres:16.x` con la versión menor fijada, `PGDATA` en el volumen, solo en la red interna `data` (sin puertos publicados), `shm_size` y límite de memoria (asumido: 512 MB), parámetros de memoria ajustados a la instancia (`shared_buffers = 128MB`, `max_connections = 30`, asumido).
- **Roles** (script idempotente en `infra/prod/initdb/`, ejecutado al crear la base y por `deploy.sh` si faltan; recibe las contraseñas por variables de entorno, nunca de ficheros, TK-086):
  - `postgres` (superusuario): solo para administración por Session Manager; la aplicación nunca lo usa;
  - `entrevecinos_owner`: propietario de la base y del esquema; lo usan **solo las migraciones** (`alembic upgrade head`); puede crear `unaccent` (extensión de confianza en PostgreSQL 13+);
  - `entrevecinos_app`: el de la API; `CONNECT`, `USAGE` del esquema y `SELECT, INSERT, UPDATE, DELETE` en tablas y `USAGE, SELECT` en secuencias, con `ALTER DEFAULT PRIVILEGES` de `entrevecinos_owner` para las tablas nuevas. Sin `CREATE`, sin `DDL`, sin `SUPERUSER`.
- **Contraseñas** de los tres roles generadas por Terraform y guardadas como `SecureString` en SSM Parameter Store (`/entrevecinos/prod/db/{postgres,owner,app}-password`), sin rotación automática; se rotan a mano (procedimiento en TK-093). Parámetros no secretos `/entrevecinos/prod/db/{host,port,name}`.
- **Copias con `pg_dump`** (`infra/prod/backup.sh` y temporizador `systemd` cada 6 horas):
  1. `docker compose exec -T db pg_dump -Fc -U entrevecinos_owner entrevecinos`, comprimido;
  2. subida en *streaming* a `s3://entrevecinos-backups-…/postgres/AAAA/MM/DD/<fecha-hora>.dump` con `--sse AES256`, sin dejar copia en disco;
  3. comprobación del tamaño mínimo y `pg_restore --list` sobre el fichero para detectar copias vacías o corruptas;
  4. métrica `Entrevecinos/Backup BackupSucceeded = 1` en CloudWatch si todo va bien (la alarma de TK-091 salta si falta durante más de 7 horas).
- **Registro de la decisión** en `infra/aws/README.md`, sección «Decisiones de arquitectura» (ver §3).

**No incluye**
- Archivado continuo del WAL (recuperación a un punto en el tiempo; ver §8).
- Ensayo de restauración (TK-092) y alarmas (TK-091).
- Migración de datos desde desarrollo (producción empieza vacía, asumido).

## 3. Requisitos técnicos

- **Decisión documentada** en `infra/aws/README.md` con este contenido mínimo:
  - qué: PostgreSQL 16 en un contenedor de la instancia, con volumen EBS propio, sin alta disponibilidad;
  - por qué: **ahorro de costes mientras el proyecto no escale**; no se necesita alta disponibilidad hasta que el proyecto sea maduro y tenga mucho tráfico;
  - impacto: RPO de 6 horas, sin conmutación por error, mantenimiento de PostgreSQL a cargo del proyecto, base y aplicación en la misma máquina;
  - **cuándo revisarla** (asumido): tráfico sostenido que satura la instancia, datos que no se pueden perder 6 horas, o más de un servidor de aplicación;
  - **evolución**: migrar a Amazon RDS (`pg_dump` / `pg_restore` con un corte de minutos), y después Multi-AZ.
- `DATABASE_URL` de la API usa `entrevecinos_app` y el *host* `db` de la red interna; las migraciones se ejecutan con una URL de `entrevecinos_owner` (TK-086). Dentro de la red de Docker no se exige TLS (no sale de la instancia).
- La instancia no publica el puerto 5432 ni lo abre en su grupo de seguridad.
- `backup.sh` con `set -euo pipefail`, sin imprimir contraseñas (usa `PGPASSWORD` desde el parámetro, nunca en la línea de comandos visible en `ps`), y registro en CloudWatch Logs.
- Actualizaciones: Dependabot (TK-089) propone las nuevas versiones menores de `postgres:16.x`; se aplican con `deploy.sh`. Un cambio de versión mayor exige `pg_dump` y `pg_restore` (procedimiento en TK-093).

## 4. Criterios de aceptación

**AC1 — Base aislada (HU-36 AC3)**
- **Given** la aplicación desplegada
- **When** reviso puertos publicados, grupo de seguridad y redes de Compose
- **Then** el puerto 5432 no está publicado ni abierto, y a la red `data` solo se unen `api` y `db`

**AC2 — Mínimo privilegio**
- **Given** una conexión como `entrevecinos_app`
- **When** intento `CREATE TABLE`, `DROP TABLE` o `ALTER TABLE`
- **Then** se deniega, y `SELECT`, `INSERT`, `UPDATE` y `DELETE` sobre las tablas de la aplicación funcionan

**AC3 — Migraciones**
- **Given** la base vacía
- **When** `deploy.sh` ejecuta `alembic upgrade head` con `entrevecinos_owner`
- **Then** todas las migraciones se aplican, incluida la extensión `unaccent`, y la API funciona con `entrevecinos_app`

**AC4 — Copias periódicas**
- **Given** el temporizador activo
- **When** pasan 6 horas
- **Then** hay una copia nueva en el bucket, cifrada, que `pg_restore --list` lee sin errores, y la métrica `BackupSucceeded` se ha publicado

**AC5 — Copias protegidas**
- **Given** una sesión en la instancia con su rol
- **When** intento borrar o sobrescribir una copia del bucket
- **Then** el borrado se deniega y la sobrescritura deja la versión anterior recuperable

**AC6 — Datos que sobreviven a la instancia**
- **Given** el volumen de datos adjunto
- **When** consulto su configuración
- **Then** es un volumen distinto del raíz, cifrado, con `DeleteOnTermination = false` y con *snapshots* diarios

**AC7 — Decisión documentada (HU-38 AC4)**
- **Given** `infra/aws/README.md`
- **When** busco cómo se ejecuta la base de datos
- **Then** encuentro que es PostgreSQL en la instancia **para ahorrar costes mientras el proyecto no escale**, su impacto, cuándo revisarla y cómo migrar a RDS

**AC8 — Sin contraseñas en el repositorio (HU-36 AC4)**
- **Given** el repositorio
- **When** busco las contraseñas de la base
- **Then** no aparecen; solo están en Parameter Store como `SecureString`

## 5. Plan de tareas

1. Volumen EBS, política de *snapshots* y bucket de copias con su política.
2. Contraseñas y parámetros en Parameter Store.
3. Script de roles (`initdb/`) y pruebas de AC2 en local con el Compose de desarrollo.
4. `backup.sh`, temporizador `systemd` y métrica.
5. Decisión en `infra/aws/README.md`.
6. Comprobación de AC1, AC3 a AC6 cuando existan TK-085 y TK-086.

## 6. Verificación

```bash
make tf-apply
aws ec2 describe-volumes --filters Name=tag:Name,Values=entrevecinos-prod-postgres --profile entrevecinos \
  --query 'Volumes[0].{enc:Encrypted,az:AvailabilityZone,att:Attachments[0].DeleteOnTermination}'
# En la instancia (Session Manager):
docker compose -f /opt/entrevecinos/docker-compose.prod.yml exec db psql -U entrevecinos_app -d entrevecinos -c 'create table x(i int)'   # permiso denegado
sudo systemctl list-timers | grep entrevecinos-backup
aws s3 ls s3://entrevecinos-backups-995006761619/postgres/ --recursive | tail -3
aws s3 rm s3://entrevecinos-backups-995006761619/postgres/<copia>   # AccessDenied
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Decisión registrada en `infra/aws/README.md` (AC7).
- [ ] `make tf-lint` y `shellcheck` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **RPO de 6 horas:** un fallo del volumen puede perder hasta 6 horas de datos (o un día si solo queda el *snapshot*). Reducirlo: copias más frecuentes (coste casi nulo) o archivado continuo del WAL a S3 con WAL-G o pgBackRest (RPO de minutos, más complejidad). Se recomienda al revisar la decisión.
- **Seguridad:** quien comprometa la instancia accede a la base (las credenciales están en la máquina). Es el riesgo principal de esta decisión; se mitiga con el usuario sin privilegios, la red interna y las copias que la instancia no puede borrar, pero no se elimina. RDS lo reduciría.
- **Memoria compartida:** web, API, proxy y PostgreSQL comparten 2 GB (`t4g.small`). Medir tras el despliegue; si falta, `t4g.medium` (+12 USD/mes, casi todo el ahorro) o ajustar límites.
- **Mantenimiento:** parches de PostgreSQL, espacio en disco y `autovacuum` quedan a cargo del proyecto; la alarma de disco de TK-091 cubre el espacio.
- **Cambio de zona de disponibilidad:** el volumen EBS solo se adjunta a instancias de su misma zona; para mover la instancia de zona hay que crear un volumen desde un *snapshot* en la otra zona (TK-092).
