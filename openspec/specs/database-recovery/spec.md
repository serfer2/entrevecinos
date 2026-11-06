# database-recovery Specification

## Purpose
Recuperación de producción: objetivos RPO y RTO, restauración desde las copias de `pg_dump`, recuperación desde *snapshot* y de imágenes borradas, con ensayos registrados.
## Requirements
### Requirement: Objetivos de recuperación
La guía de producción SHALL fijar un RPO de 6 horas (la última copia de `pg_dump`) y un RTO de 4 horas, y los ensayos MUST cumplirlos.

#### Scenario: Objetivos en la guía
- **WHEN** consulto `infra/aws/README.md`
- **THEN** encuentro el RPO, el RTO y el registro del último ensayo

### Requirement: Restauración desde una copia
`infra/prod/restore.sh <clave>` SHALL restaurar una copia de `backup.sh` en una base nueva (por defecto `entrevecinos_restore`) como `entrevecinos_owner`, aplicar los permisos de `entrevecinos_app` y mostrar los recuentos de `users`, `community`, `listing` y `media_asset`, sin tocar la base de producción. Con `--production` MUST exigir `--yes`, hacer antes una copia de la base actual, parar la API, sustituir la base por la restaurada conservando la anterior y arrancar la API. MUST NOT admitir bases que no empiecen por `entrevecinos_` ni escribir contraseñas en ficheros.

#### Scenario: Ensayo
- **WHEN** ejecuto `restore.sh --target entrevecinos_restore <copia>`
- **THEN** la base restaurada tiene los datos de la copia y producción no cambia

#### Scenario: Producción sin confirmación
- **WHEN** ejecuto `restore.sh --production <copia>` sin `--yes`
- **THEN** termina con error sin hacer nada

#### Scenario: Sustitución de producción
- **WHEN** ejecuto `restore.sh --production --yes <copia>`
- **THEN** la base `entrevecinos` tiene los datos de la copia, la anterior queda como `entrevecinos_anterior_<fecha>` y la API vuelve a funcionar

### Requirement: Recuperación desde snapshot
La guía SHALL describir cómo crear un volumen desde el último *snapshot* del volumen de datos, montarlo en la instancia y arrancar PostgreSQL sobre él, y los volúmenes de ensayo MUST borrarse al terminar.

#### Scenario: Ensayo desde snapshot
- **WHEN** creo un volumen desde el último *snapshot* y arranco PostgreSQL en un contenedor aparte sobre él
- **THEN** los datos son los del momento del *snapshot* y no queda ningún volumen de ensayo

### Requirement: Recuperación de imágenes
La guía SHALL describir cómo recuperar una imagen borrada del bucket de imágenes a partir de su versión anterior (30 días).

#### Scenario: Imagen borrada
- **WHEN** borro la imagen de un anuncio y sigo el procedimiento
- **THEN** el objeto vuelve a existir y el anuncio la muestra

