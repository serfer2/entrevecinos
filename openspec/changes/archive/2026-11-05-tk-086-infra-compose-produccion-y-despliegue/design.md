## Context

La instancia de TK-085 tiene Docker, Compose, el volumen de PostgreSQL montado y un rol que lee `/entrevecinos/prod/*`, descarga de ECR y escribe en `/entrevecinos/prod/app/*`. Los secretos (TK-082, TK-083) están en Parameter Store. CloudFront (TK-087) y GitHub Actions (TK-090) llegan después; hasta entonces se despliega a mano y se prueba desde la propia instancia.

## Goals / Non-Goals

**Goals:** Compose de producción endurecido, despliegue idempotente por SSM con migraciones, salud y vuelta atrás, y ningún secreto en disco.

**Non-Goals:** CloudFront (TK-087), despliegue continuo (TK-090), alarmas y paneles (TK-091), *runbook* de rotación y restauración (TK-093).

## Decisions

- **Ficheros dentro del documento de SSM.** Terraform incrusta en `entrevecinos-deploy` (base64) el Compose y `infra/prod/`; el documento los escribe en `/opt/entrevecinos` y ejecuta `deploy.sh`. Alternativas: descargarlos de S3 (otro bucket o prefijo y más permisos) o de GitHub (credenciales o repositorio público). Así la versión del documento es la de la configuración, sin permisos nuevos; a cambio, cambiar el Compose exige `make tf-apply` antes de desplegar. Los *digests* se validan con `allowedPattern` (sin inyección en el *shell*).
- **Mismo árbol en el repositorio y en la instancia:** `/opt/entrevecinos/docker-compose.prod.yml` y `/opt/entrevecinos/prod/…`, así las rutas relativas del Compose (`./prod/proxy`, `./prod/initdb`) valen en los dos sitios.
- **Secretos al entorno con una sola llamada** (`get-parameters --with-decryption`), leídos con `read` desde la salida del comando (tubería, sin ficheros). Las imágenes van por variables (`API_IMAGE`, `WEB_IMAGE`) con el *digest*. Los valores no secretos (dominio, bucket, remitente, *configuration set*) se escriben en el Compose.
- **Credenciales de ECR con `amazon-ecr-credential-helper`** (paquete de Amazon Linux): Docker obtiene el token con el rol cuando lo necesita y no queda ninguno en `~/.docker/config.json`, a diferencia de `docker login`.
- **Operación sin Compose.** Con `${VAR:?}`, cualquier orden de `docker compose` sin los secretos falla (es lo que se busca). `backup.sh` y la operación diaria usan `docker` con las etiquetas de Compose (`com.docker.compose.service=db`).
- **Redes:** `edge` (proxy y web), `internal` (web y api, interna), `data` (api y db, interna) y `egress` (solo api): la API necesita salir a S3, SES e IMDS y las redes internas no tienen salida. La web y la base de datos no salen a Internet.
- **Proxy nginx sin *root*** (`nginxinc/nginx-unprivileged`, usuario 101, puerto `8080` publicado como `80`). Se descartó Caddy, que propone el ticket: su binario oficial tiene la capacidad de fichero `cap_net_bind_service` y, sin *root* y con `no-new-privileges` (activo también en todo el *daemon*), no llega a ejecutarse (`operation not permitted`); como *root* sin capacidades sí arranca, pero incumple «sin *root*», y una imagen propia exigiría otro repositorio de ECR. El *entrypoint* de nginx sustituye solo `${ORIGIN_VERIFY}` (`NGINX_ENVSUBST_FILTER`) y escribe la configuración en un `tmpfs`, así que el secreto no toca el disco. Resuelve `web` con el DNS de Docker en cada petición (su IP cambia al desplegar). Su *healthcheck* usa un segundo puerto solo dentro del contenedor, para no abrir ninguna ruta sin cabecera en el `8080`.
- **PostgreSQL:** datos en `PGDATA=/var/lib/postgresql/data/pgdata`, un subdirectorio del volumen montado (la imagen necesita un directorio vacío). `cap_drop: ALL` y solo `CHOWN`, `DAC_OVERRIDE`, `FOWNER`, `SETGID` y `SETUID`, que usa su *entrypoint*. Los roles se crean al inicializar (`initdb`) y en cada despliegue con `docker exec`, pasando las contraseñas solo a esa orden.
- **Migraciones** con `docker compose run --rm --no-deps api alembic upgrade head` y `DATABASE_URL` de `entrevecinos_owner` por entorno (`-e DATABASE_URL` sin valor: no aparece en la línea de órdenes). Las contraseñas son alfanuméricas (TK-082), así que no hace falta codificarlas en la URL.
- **Cabecera en la comprobación de salud** con `curl -H @-` desde la entrada estándar, para que el valor no aparezca en la lista de procesos.
- **Parámetro `origin-verify` en el estado.** A diferencia de las contraseñas, CloudFront (TK-087) necesita el valor como cabecera de origen, que no es un argumento de solo escritura: se genera con `random_password` y queda en el estado (bucket privado, cifrado y versionado). Solo sirve para que nadie salte CloudFront; no da acceso a datos.
- **Logs:** grupos `/entrevecinos/prod/app/{proxy,web,api,db,deploy}` creados por Terraform (30 días); el rol no puede crear grupos.
- **Límites (instancia de 2 GB):** `db` 512 MB, `api` 384 MB, `web` 512 MB, `proxy` 64 MB; el resto queda para el sistema y la caché.

## Risks / Trade-offs

- [Docker guarda el entorno de cada contenedor en `/var/lib/docker` y `docker inspect` lo muestra] → solo *root*; `deploy` no pertenece al grupo `docker` (TK-085). Mejora futura: que la API lea los secretos al arrancar.
- [Corte de segundos en cada despliegue (una sola instancia)] → aceptable en el MVP.
- [La vuelta atrás no deshace migraciones] → migraciones compatibles con la versión anterior (*expand/contract*), documentado en TK-093.
- [Cambiar el Compose exige `tf-apply`] → documentado en «Despliegue»; TK-090 lo encadena.
- [Docker Hub limita las descargas anónimas] → pocas imágenes y fijadas por versión; si molesta, caché de ECR (*pull through cache*).
