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
Los contenedores SHALL enviar sus logs con el *driver* `awslogs` a `/entrevecinos/prod/app/<servicio>`, con retención de 14 días; la salida de cada despliegue MUST quedar en `/entrevecinos/prod/app/deploy` (30 días) y la de las copias en `/entrevecinos/prod/app/backup` (14 días). El proxy MUST registrar el método, la ruta sin la cadena de consulta y el protocolo, nunca la petición completa.

#### Scenario: Logs de la API
- **WHEN** la API atiende peticiones
- **THEN** sus logs aparecen en `/entrevecinos/prod/app/api`

#### Scenario: Proxy sin cadena de consulta
- **WHEN** alguien abre `/verificar-correo?token=…`
- **THEN** el registro del proxy muestra `GET /verificar-correo HTTP/1.1`

### Requirement: Límite de peticiones en el proxy
El proxy SHALL identificar al visitante por el último valor de `X-Forwarded-For` (el que añade CloudFront) y MUST responder `429` cuando una IP supera 20 peticiones `POST` en 5 minutos (con ráfaga de 10) a `/iniciar-sesion` y `/registro`, o 5 peticiones por segundo (con ráfaga de 100) en total. Los rechazos y el registro de accesos SHALL aparecer en `/entrevecinos/prod/app/proxy` con la IP del visitante.

#### Scenario: Fuerza bruta en el inicio de sesión
- **WHEN** envío desde una IP más de 11 `POST` seguidos a `/iniciar-sesion`
- **THEN** el proxy responde `429` y el rechazo aparece en `/entrevecinos/prod/app/proxy`

#### Scenario: X-Forwarded-For falseado
- **WHEN** el visitante envía su propio `X-Forwarded-For` con otra IP
- **THEN** el límite se aplica a la IP que añade CloudFront

### Requirement: Copia antes de migrar
`deploy.sh` SHALL ejecutar `backup.sh` antes de aplicar las migraciones cuando la base ya tiene esquema y hay migraciones pendientes, y si la copia falla MUST terminar con error sin migrar ni cambiar los contenedores.

#### Scenario: Migración pendiente
- **WHEN** despliego una versión con una migración nueva
- **THEN** hay una copia nueva en el bucket antes de que se aplique

#### Scenario: Sin migraciones
- **WHEN** despliego una versión sin migraciones nuevas
- **THEN** no se hace copia previa

