# TK-092 · Infraestructura: copias de seguridad y recuperación probada

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / operación |
| **Componente** | `infra/aws/README.md` (procedimientos), `infra/prod/restore.sh` (nuevo), `infra/aws/modules/database/` y `infra/aws/modules/storage/` (ajustes) |
| **Historia** | HU-38 Vigilar, recuperar y operar producción (Épica 13) |
| **Prioridad** | Media |
| **Depende de** | TK-082, TK-091 |
| **Referencias** | `readme.md` §2.5 («programar copias periódicas y comprobar que es posible restaurarlas»); TK-001 §8 (copias pendientes para producción); TK-082 (copias con `pg_dump` y *snapshots*) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El README pide copias de seguridad con política de retención y comprobar que se pueden restaurar. Mientras el proyecto no escale, PostgreSQL corre en la instancia (TK-082) con dos tipos de copia: `pg_dump` cada 6 horas en S3 (30 días) y *snapshots* diarios del volumen de datos (7 días). Las imágenes de los anuncios tienen versionado en S3 (TK-080). Una copia que nunca se ha restaurado no garantiza nada.

**Objetivo:** fijar los objetivos de recuperación, automatizar y documentar la restauración de la base de datos y de las imágenes, ensayarla y dejar el resultado registrado.

## 2. Alcance

**Incluye**
- Objetivos del MVP (asumido): **RPO** 6 horas (última copia de `pg_dump`); **RTO** 4 horas.
- `infra/prod/restore.sh <clave-s3>`: descarga una copia, para `api`, recrea la base con `pg_restore --clean --if-exists` como `entrevecinos_owner`, vuelve a aplicar los permisos de `entrevecinos_app` y arranca `api`. Con `--target <base>` restaura en una base aparte (`entrevecinos_restore`) para ensayos sin tocar producción.
- Procedimientos documentados en `infra/aws/README.md`:
  1. **Error de datos** (borrado o corrupción lógica): restaurar la copia de `pg_dump` anterior al error en `entrevecinos_restore`, comprobarla y sustituir la de producción (o copiar solo las filas afectadas).
  2. **Fallo del volumen de datos:** crear un volumen desde el último *snapshot*, adjuntarlo en lugar del dañado y aplicar encima la copia de `pg_dump` más reciente si es posterior al *snapshot*.
  3. **Pérdida de la instancia** (o cambio de zona de disponibilidad): crear la instancia con Terraform (TK-085), adjuntar el volumen existente o uno creado desde *snapshot* en la nueva zona, y desplegar (TK-086).
  4. **Imagen borrada:** restaurar la versión anterior del objeto en el bucket de imágenes.
- Copia manual (`backup.sh` a demanda) antes de cada migración destructiva, como paso de `deploy.sh` o de la guía (asumido).
- Ensayo real de los procedimientos 1 y 2 con datos de prueba y registro del resultado (fecha, copia usada, tiempo empleado, incidencias) en `infra/aws/README.md`. Se repite cada 3 meses (asumido).

**No incluye**
- Archivado continuo del WAL ni recuperación a un punto en el tiempo (ver TK-082 §8).
- AWS Backup ni copias en otra región o cuenta (ver §8).

## 3. Requisitos técnicos

- `restore.sh`, como `deploy.sh` y `backup.sh`, lee las contraseñas de Parameter Store en el entorno de su proceso y nunca las escribe en ficheros (TK-086).
- `restore.sh` pide confirmación explícita (`--yes`) antes de sobrescribir la base de producción y siempre hace antes una copia de la base actual.
- El ensayo no deja recursos de pago encendidos: los volúmenes creados desde *snapshot* para el ensayo se borran al terminar.
- Los procedimientos se escriben con comandos que se pueden copiar (Session Manager, `aws ec2 create-volume --snapshot-id`, `attach-volume`), con marcadores `<…>` solo para los identificadores.

## 4. Criterios de aceptación

**AC1 — Restauración de una copia probada (HU-38 AC3)**
- **Given** datos creados en producción y una copia de `pg_dump` posterior
- **When** ejecuto `restore.sh --target entrevecinos_restore <copia>`
- **Then** la base restaurada contiene esos datos (recuentos de `users`, `communities` y `listings`) y el tiempo empleado está por debajo del RTO

**AC2 — Recuperación del volumen probada (HU-38 AC3)**
- **Given** el último *snapshot* del volumen de datos
- **When** creo un volumen desde él y lo monto en la instancia en modo de solo lectura en otro punto de montaje
- **Then** PostgreSQL arranca sobre él en un contenedor aparte y los datos son los del momento del *snapshot*

**AC3 — Imagen recuperada**
- **Given** una imagen de un anuncio borrada del bucket
- **When** sigo el procedimiento de recuperación
- **Then** el anuncio vuelve a mostrar la imagen

**AC4 — Ensayo registrado (HU-38 AC4)**
- **Given** `infra/aws/README.md`
- **When** lo consulto
- **Then** encuentro los procedimientos, los objetivos RPO/RTO y el registro del último ensayo

## 5. Plan de tareas

1. Objetivos RPO/RTO y procedimientos por escrito.
2. `restore.sh` con modo de ensayo.
3. Ensayo de restauración desde `pg_dump` (AC1).
4. Ensayo desde *snapshot* (AC2) y de recuperación de una imagen (AC3).
5. Registro del resultado y limpieza de los recursos de ensayo.

## 6. Verificación

```bash
aws s3 ls s3://entrevecinos-backups-995006761619/postgres/ --recursive --profile entrevecinos | tail -1
# En la instancia (Session Manager):
sudo /opt/entrevecinos/restore.sh --target entrevecinos_restore postgres/<AAAA/MM/DD>/<copia>.dump
aws ec2 describe-snapshots --owner-ids self --filters Name=tag:Name,Values=entrevecinos-prod-postgres --profile entrevecinos \
  --query 'reverse(sort_by(Snapshots,&StartTime))[0].{id:SnapshotId,t:StartTime}'
aws s3api list-object-versions --bucket entrevecinos-media-995006761619 --prefix <clave> --profile entrevecinos
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] No quedan volúmenes ni bases de ensayo.
- [ ] `shellcheck` sin avisos en `restore.sh`.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Copias en la misma cuenta y región:** un borrado con credenciales de administrador o un fallo de la región se llevaría todo. La instancia no puede borrar copias (TK-082), pero un administrador sí. El plan del proyecto no admite copias entre regiones; S3 Object Lock en modo *governance* sobre el bucket de copias impediría también el borrado por error de un administrador, con coste casi nulo. Se deja como mejora.
- **Retención de 30 días:** un error de datos detectado más tarde no se puede deshacer. Ampliarla cuesta céntimos con una base pequeña; decidir al refinar.
- **RPO de 6 horas:** consecuencia de la decisión de TK-082 (ahorro mientras el proyecto no escale); al migrar a RDS se pasa a recuperación a un punto en el tiempo.
