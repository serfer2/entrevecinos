# production-deployment Specification

## Purpose
Despliegue de la aplicación en la instancia de producción: Compose con proxy de origen, web, API y PostgreSQL endurecidos, despliegue por SSM con migraciones, comprobación de salud y vuelta atrás, secretos solo por entorno y logs en CloudWatch.
## Requirements
### Requirement: Despliegue completo por SSM
El documento de SSM `entrevecinos-deploy` SHALL copiar a `/opt/entrevecinos` el Compose de producción y `infra/prod/`, y ejecutar `deploy.sh` con los *digests* de `api` y `web`, que MUST validarse como `sha256:` seguido de 64 caracteres hexadecimales. `deploy.sh` SHALL descargar las imágenes de ECR, crear o actualizar los roles de PostgreSQL, aplicar las migraciones como `entrevecinos_owner`, arrancar los servicios y comprobar que `api` y `web` están *healthy* y que la web responde a través del proxy.

#### Scenario: Despliegue correcto
- **WHEN** ejecuto `entrevecinos-deploy` con los *digests* de imágenes nuevas
- **THEN** las migraciones se aplican, `web` y `api` quedan *healthy*, la web responde por el proxy y el comando termina bien

#### Scenario: Digest no válido
- **WHEN** ejecuto el documento con un `ApiDigest` que no es `sha256:<64 hex>`
- **THEN** SSM rechaza el comando sin ejecutar nada en la instancia

### Requirement: Vuelta atrás automática
Si las imágenes nuevas no quedan *healthy* o la web no responde, `deploy.sh` SHALL volver a los *digests* guardados en `/opt/entrevecinos/current-digests` (que MUST contener solo *digests*) y MUST terminar con error. Las migraciones no se deshacen.

#### Scenario: API que no arranca
- **WHEN** despliego una imagen de la API que no supera el *healthcheck*
- **THEN** se restauran los *digests* anteriores, la web sigue respondiendo y el comando termina con error

### Requirement: Solo el proxy expuesto
Solo `proxy` SHALL publicar un puerto (`80`). `api` MUST ser accesible solo desde `web` (red `internal`), y `db` solo desde `api` (red `data`); desde `web` MUST NOT resolverse `db`.

#### Scenario: Puertos publicados
- **WHEN** reviso los puertos publicados y la resolución de nombres en la instancia
- **THEN** solo el puerto 80 del proxy está publicado y desde `web` no se resuelve `db`

### Requirement: Cabecera de origen
El proxy SHALL responder `403` a cualquier petición sin la cabecera `X-Origin-Verify` con el valor de `/entrevecinos/prod/origin-verify`, sin reenviarla a la web, y MUST quitar esa cabecera de las peticiones que reenvía.

#### Scenario: Sin cabecera
- **WHEN** pido `http://127.0.0.1/` en la instancia sin la cabecera
- **THEN** recibo `403`

#### Scenario: Con cabecera
- **WHEN** pido `http://127.0.0.1/` con la cabecera correcta
- **THEN** responde la web

### Requirement: Contenedores endurecidos
`proxy`, `web` y `api` SHALL ejecutarse sin *root*, con el sistema de ficheros raíz de solo lectura, sin capacidades, con `no-new-privileges`, con límites de memoria y CPU y sin el socket de Docker. `db` MUST tener `no-new-privileges` y solo las capacidades que necesita la imagen oficial.

#### Scenario: Inspección
- **WHEN** inspecciono los contenedores con `docker inspect`
- **THEN** `proxy`, `web` y `api` tienen `ReadonlyRootfs`, `CapDrop` `ALL`, `no-new-privileges` y ningún montaje de `docker.sock`

### Requirement: Secretos solo por entorno
`deploy.sh` SHALL leer los secretos de Parameter Store y pasarlos a `docker compose` solo como variables de entorno de su propio proceso. MUST NOT escribirse ningún secreto en disco (ni `.env`, ni ficheros de contraseñas, ni temporales) ni en la salida del despliegue, y el Compose MUST fallar si falta alguno (`${VAR:?}`).

#### Scenario: Búsqueda de secretos
- **WHEN** busco el valor de los secretos en `/opt/entrevecinos` y `/tmp`, y en la salida del despliegue en CloudWatch
- **THEN** no aparecen y no existe ningún `.env`

#### Scenario: Compose sin secretos
- **WHEN** ejecuto `docker compose up` sin las variables de los secretos
- **THEN** falla sin arrancar ningún contenedor

### Requirement: Logs en CloudWatch
Los contenedores SHALL enviar sus logs con el *driver* `awslogs` a `/entrevecinos/prod/app/<servicio>`, y la salida de cada despliegue MUST quedar en `/entrevecinos/prod/app/deploy`.

#### Scenario: Logs de la API
- **WHEN** la API atiende peticiones
- **THEN** sus logs aparecen en `/entrevecinos/prod/app/api`

