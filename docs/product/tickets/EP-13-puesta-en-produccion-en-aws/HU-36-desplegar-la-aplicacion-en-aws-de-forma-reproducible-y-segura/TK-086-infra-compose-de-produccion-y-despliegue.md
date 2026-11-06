# TK-086 · Infraestructura: Docker Compose de producción y script de despliegue

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | `infra/docker-compose.prod.yml` (nuevo), `infra/prod/` (nuevo: `Caddyfile`, `deploy.sh`), documento de SSM en `infra/aws/modules/compute/`, `apps/web/Dockerfile` (si hace falta) |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-081, TK-085 |
| **Referencias** | `infra/docker-compose.yml`; etapas `prod` de `apps/api/Dockerfile` y `apps/web/Dockerfile`; TK-046 (CSP y `STORAGE_PUBLIC_URL`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`infra/docker-compose.yml` es de desarrollo: construye las etapas `dev`, monta el código y levanta PostgreSQL, MinIO y Mailpit. En producción la instancia ejecuta `proxy`, `web`, `api` y `db` (PostgreSQL 16, TK-082, mientras el proyecto no escale), con las imágenes `prod` de ECR, los datos de PostgreSQL en su volumen EBS, las imágenes en S3 y el correo en SES. No hay MinIO ni Mailpit.

El navegador solo habla con Next.js; la API se llama desde el servidor de Next (`API_INTERNAL_URL`), así que la API no se publica.

**Objetivo:** un Compose de producción seguro y un script de despliegue idempotente, con migraciones, comprobación de salud y vuelta atrás, que se ejecuta en la instancia por SSM.

## 2. Alcance

**Incluye**
- `infra/docker-compose.prod.yml`:
  - `proxy` (Caddy, imagen fijada por versión): escucha en `:80`, rechaza con `403` cualquier petición sin la cabecera `X-Origin-Verify` con el valor secreto de CloudFront (TK-087) y reenvía a `web:3000`; sin TLS (lo termina CloudFront);
  - `web`: imagen `…/entrevecinos/web@sha256:…`, `API_INTERNAL_URL=http://api:8000/v1`, `STORAGE_PUBLIC_URL` del bucket;
  - `api`: imagen `…/entrevecinos/api@sha256:…`, `ENVIRONMENT=production`, `DATABASE_URL` con `entrevecinos_app@db:5432`, variables de TK-081 (`MAIL_BACKEND=ses`, `STORAGE_ADDRESSING_STYLE=virtual`, `STORAGE_REGION=eu-north-1`…), sin puerto publicado, `depends_on: db: condition: service_healthy`;
  - `db`: `postgres:16.x` fijada por versión, datos en `/srv/entrevecinos/postgres` (volumen EBS de TK-082), *scripts* de `infra/prod/initdb/` montados en `/docker-entrypoint-initdb.d`, contraseñas de `postgres`, `entrevecinos_owner` y `entrevecinos_app` por variables de entorno (`POSTGRES_PASSWORD`… solo se usan al inicializar la base y al crear los roles), `pg_isready` como *healthcheck*, límite de memoria, sin puertos publicados;
  - redes: `edge` (proxy ↔ web), `internal` (web ↔ api, `internal: true`) y `data` (api ↔ db, `internal: true`): la web no llega a la base de datos;
  - endurecimiento en `proxy`, `web` y `api` (en `db`, solo `no-new-privileges` y `cap_drop` con las capacidades que necesita la imagen oficial): `read_only: true` con `tmpfs` donde haga falta (`/tmp`, caché de Next), `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, usuario no root (ya en los Dockerfiles), límites de memoria y CPU, `restart: unless-stopped`, *healthchecks*;
  - `logging: driver: awslogs` con un grupo por servicio (`/entrevecinos/prod/{proxy,web,api}`).
- `infra/prod/deploy.sh` (en la instancia, `/opt/entrevecinos`), invocado con los *digests* de `api` y `web`:
  1. `aws ecr get-login-password | docker login` con el rol de la instancia;
  2. lee los parámetros de `/entrevecinos/prod/` de Parameter Store (secretos con `--with-decryption`) y los **exporta solo como variables de entorno del propio proceso** de `deploy.sh`, que las pasa a `docker compose` (interpolación `${VAR}` en `docker-compose.prod.yml`, sin `env_file`). **No se escribe ningún secreto en disco**: ni `.env`, ni ficheros de contraseñas, ni ficheros temporales;
  3. `docker compose pull` y `docker compose up -d db` (espera a *healthy*); crea los roles de TK-082 si faltan;
  4. `docker compose run --rm -e DATABASE_URL=<url de entrevecinos_owner> api alembic upgrade head`;
  5. `docker compose up -d --remove-orphans`;
  6. espera a que `api` y `web` estén *healthy* y comprueba `http://127.0.0.1/` con la cabecera de origen;
  7. si falla, vuelve a los *digests* anteriores (`/opt/entrevecinos/current-digests`, que solo contiene los *digests*, nunca secretos) y termina con error;
  8. guarda los *digests* desplegados y limpia imágenes antiguas (`docker image prune`).
- Instalación de `backup.sh` y su temporizador `systemd` de TK-082 en cada despliegue (idempotente). Incluye la primera copia real en la instancia y su comprobación con `pg_restore --list` (AC4 de TK-082, trasladado aquí porque necesita la instancia y el contenedor `db`).
- Documento de SSM `entrevecinos-deploy` (Terraform) que copia los ficheros de `infra/prod/` y ejecuta `deploy.sh` con los parámetros `ApiDigest` y `WebDigest`.
- Primer despliegue manual: construir y subir las imágenes desde el equipo y lanzar el documento con `aws ssm send-command`.

**No incluye**
- CloudFront y el valor final de la cabecera secreta (TK-087).
- Automatización desde GitHub Actions (TK-090).

## 3. Requisitos técnicos

- La web se construye para `linux/arm64` (instancia Graviton); `NEXT_PUBLIC_API_BASE_URL` no se usa en el navegador, pero el `ARG` debe tener un valor coherente.
- El valor de la cabecera de origen se guarda en Parameter Store como `SecureString` (`/entrevecinos/prod/origin-verify`) y lo comparten CloudFront (TK-087) y el proxy, que lo recibe por entorno (`{env.ORIGIN_VERIFY}` en el `Caddyfile`).
- **Secretos solo por entorno:**
  - `docker-compose.prod.yml` declara los secretos como `${VAR:?}` (falla si faltan) y no usa `env_file`; el fichero se versiona sin ningún valor secreto;
  - `deploy.sh` desactiva la traza (`set +x`), no ejecuta `docker compose config` (imprimiría los valores) y descarta las variables al terminar;
  - cualquier recreación de contenedores (`up -d` con cambios) se hace siempre a través de `deploy.sh`, que vuelve a leer Parameter Store; un `docker compose up` manual sin esas variables falla en vez de arrancar sin secretos;
  - tras un reinicio de la instancia, Docker vuelve a arrancar los contenedores existentes (`restart: unless-stopped`) con su configuración guardada, sin necesidad de `deploy.sh`;
  - **rotar un secreto** exige volver a ejecutar `deploy.sh` para recrear los contenedores afectados (procedimiento en TK-093).
- `docker compose up -d` de una versión nueva **no** reinicia `db` salvo que cambie su imagen o su configuración; las actualizaciones de PostgreSQL se despliegan aparte, con copia previa (`backup.sh`).
- Las migraciones son compatibles hacia atrás con la versión anterior de la API (los *rollbacks* no deshacen migraciones); queda documentado en TK-093.
- Script con `set -euo pipefail`, sin imprimir secretos y con registro en CloudWatch a través de SSM.
- Si `read_only` rompe Next.js (escritura en `.next/cache`), montar un `tmpfs` en esa ruta.

## 4. Criterios de aceptación

**AC1 — Despliegue completo (HU-36 AC2)**
- **Given** imágenes nuevas en ECR
- **When** ejecuto el documento `entrevecinos-deploy` con sus *digests*
- **Then** las migraciones se aplican, `web` y `api` quedan *healthy* y la web responde en la instancia a través del proxy

**AC2 — API y base de datos no expuestas (HU-36 AC3)**
- **Given** la aplicación en marcha
- **When** reviso los puertos publicados en la instancia
- **Then** solo el proxy escucha en el puerto 80, la API solo es accesible desde la red interna de Compose y PostgreSQL solo desde la red `data` (desde `web` no se resuelve `db`)

**AC3 — Cabecera de origen**
- **Given** el proxy
- **When** llega una petición sin la cabecera `X-Origin-Verify` correcta
- **Then** responde `403` sin reenviarla a la web

**AC4 — Vuelta atrás (HU-37 AC4)**
- **Given** una imagen nueva cuya API no supera el *healthcheck*
- **When** se despliega
- **Then** el script restaura los *digests* anteriores, la web sigue funcionando y el comando termina con error

**AC5 — Contenedores endurecidos**
- **Given** los contenedores `proxy`, `web` y `api` en marcha
- **When** los inspecciono (`docker inspect`)
- **Then** tienen el sistema de ficheros raíz de solo lectura, sin capacidades, con `no-new-privileges` y sin el socket de Docker montado

**AC6 — Ningún secreto en ficheros de la instancia (HU-36 AC4)**
- **Given** la aplicación desplegada
- **When** busco los valores de los secretos en `/opt/entrevecinos`, `/tmp` y el directorio del usuario `deploy`, y reviso la salida de `deploy.sh` en CloudWatch
- **Then** no aparecen; no existe ningún `.env` ni fichero de contraseñas, y los contenedores reciben los secretos solo por entorno

## 5. Plan de tareas

1. `docker-compose.prod.yml` y `Caddyfile`.
2. `deploy.sh` con lectura de secretos, migraciones, salud y vuelta atrás.
3. Documento de SSM en Terraform.
4. Construcción `arm64` y primer despliegue manual.
5. Pruebas de AC3 a AC5.

## 6. Verificación

```bash
docker buildx build --platform linux/arm64 --target prod -t <ecr>/entrevecinos/api:<sha> --push apps/api
docker buildx build --platform linux/arm64 --target prod -t <ecr>/entrevecinos/web:<sha> --push apps/web
aws ssm send-command --document-name entrevecinos-deploy --targets Key=InstanceIds,Values=<id> \
  --parameters ApiDigest=<sha256>,WebDigest=<sha256> --profile entrevecinos
# En la instancia (SSM):
docker compose -f /opt/entrevecinos/docker-compose.prod.yml ps
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/                                  # 403
curl -s -o /dev/null -w '%{http_code}\n' -H 'X-Origin-Verify: <valor>' http://127.0.0.1/    # 200/307
sudo find /opt/entrevecinos /tmp /home/deploy -name '*.env' -o -name '*password*'           # sin resultados
sudo grep -rlF "$(aws ssm get-parameter --name /entrevecinos/prod/jwt-secret --with-decryption --query Parameter.Value --output text)" /opt/entrevecinos /tmp /home/deploy   # sin resultados
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `docker compose -f infra/docker-compose.prod.yml config` válido.
- [ ] `shellcheck` sin avisos en `deploy.sh`.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Secretos solo por entorno (decisión):** se descarta el `.env` en disco; los secretos van de Parameter Store al entorno del proceso de Compose y de ahí a los contenedores. **Riesgo residual:** Docker guarda la configuración de cada contenedor, variables de entorno incluidas, en `/var/lib/docker/containers/<id>/config.v2.json` (solo legible por *root*, en el EBS cifrado), y cualquiera con acceso al *daemon* de Docker las ve con `docker inspect`; además, un proceso comprometido dentro de un contenedor lee su propio entorno. Por eso el usuario `deploy` no pertenece al grupo `docker` (`deploy.sh` lo ejecuta el agente de SSM como *root*) y ningún usuario interactivo tiene acceso a Docker.
- **Alternativa más fuerte para el futuro:** que la API y el proxy lean los secretos de Parameter Store al arrancar con el rol de la instancia (cambio de código en TK-081 y configuración del proxy), de modo que no estén ni en el entorno ni en la configuración de Docker. Se deja como mejora cuando el proyecto escale.
- **Caddy frente a nginx:** Caddy tiene una configuración más corta y segura por defecto; nginx es más conocido. Cualquiera sirve; también podría prescindirse del proxy y comprobar la cabecera en `proxy.ts` de Next, pero mezclaría infraestructura y aplicación.
- **Corte durante el despliegue:** con una sola instancia, `up -d` reinicia los contenedores (segundos sin servicio). Aceptable en el MVP; un despliegue *blue/green* con dos juegos de contenedores detrás del proxy lo evitaría.
- **Migraciones incompatibles:** si una migración rompe la versión anterior, la vuelta atrás no basta. Se exige que sean compatibles (patrón *expand/contract*).
