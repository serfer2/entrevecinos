# TK-019 · Infraestructura: almacenamiento de imágenes con MinIO

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | `infra/` (`docker-compose.yml`, `storage/`), `apps/api` (configuración), `Makefile` |
| **Historia** | HU-07 Publicar un anuncio (Épica 3) — fotografías |
| **Prioridad** | Alta (bloquea TK-021) |
| **Depende de** | TK-001, TK-002, TK-004 |
| **Referencias** | `readme.md` §2.1, §2.2 (MinIO compatible con S3), §2.4, §2.5 (aislamiento y secretos); TK-002 §3.8 (decisión abierta sobre el volumen de assets); `docs/api/paths/media_asset_id.yaml` (URL prefirmada) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-07 permite adjuntar fotografías. El README define MinIO (compatible con S3) como almacenamiento de imágenes, con PostgreSQL guardando solo los metadatos, y el contrato sirve las imágenes con una redirección a una URL prefirmada. TK-002 dejó un volumen local `api_assets` como paso previo. **Decisión tomada: MinIO.**

**Objetivo:** añadir MinIO al entorno de desarrollo con un *bucket* privado y credenciales propias para la API, y retirar el volumen `api_assets`.

## 2. Alcance

**Incluye**
- Servicio `storage` (MinIO) con volumen `storage_data`, en la red interna `data`.
- Servicio de un solo uso `storage-init` (cliente `mc`) que crea el *bucket*, un usuario para la API y su política.
- Variables en `.env.example` y en el servicio `api`.
- Publicación del puerto S3 solo en `127.0.0.1`, para que el navegador pueda abrir las URL prefirmadas en local.
- Retirada del volumen `api_assets` y de `ASSETS_DIR`.
- `infra/README.md` actualizado.

**No incluye**
- Cliente S3 en la API, subida y lectura de ficheros (TK-021).
- Almacenamiento de producción (S3 gestionado, entrega 3).

## 3. Requisitos técnicos

### 3.1 Servicios

- `storage`: imagen `pgsty/minio:RELEASE.2026-08-04T00-00-00Z` (ver §3.6), `command: server /data --console-address :9001`, volumen `storage_data:/data`, *healthcheck* `mc ready local` o `curl -f http://127.0.0.1:9000/minio/health/live`, `restart: unless-stopped`.
  - Redes: `data` (para la API) y `edge` (solo para poder publicar el puerto, ver §3.3).
  - Puertos: `127.0.0.1:${STORAGE_HOST_PORT:-9000}:9000`. La consola (`9001`) **no** se publica; para depurar se documenta un *override* opcional como el de la base de datos (TK-001).
- `storage-init`: la **misma imagen** que `storage` con `entrypoint: ["sh"]` (incluye `mc`; así no hay que fijar ni actualizar una segunda imagen), `depends_on: storage (healthy)`, `restart: "no"`. Ejecuta un script idempotente `infra/storage/init.sh`:
  1. `mc alias set local http://storage:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD`
  2. `mc mb --ignore-existing local/$STORAGE_BUCKET` (privado: sin política anónima)
  3. Crea el usuario `$STORAGE_ACCESS_KEY` y le asigna una política que solo permite `s3:GetObject`, `s3:PutObject` y `s3:DeleteObject` sobre `arn:aws:s3:::$STORAGE_BUCKET/*` (`infra/storage/api-policy.json`).
- `api`: `depends_on` añade `storage-init: condition: service_completed_successfully`.

### 3.2 Variables (`.env.example`, valores ficticios)

```dotenv
# --- Almacenamiento (MinIO) ---
MINIO_ROOT_USER=entrevecinos-root
MINIO_ROOT_PASSWORD=change-me-root-password
STORAGE_BUCKET=entrevecinos-media
STORAGE_ACCESS_KEY=entrevecinos-api
STORAGE_SECRET_KEY=change-me-api-secret
STORAGE_HOST_PORT=9000
```

En el servicio `api`: `STORAGE_ENDPOINT=http://storage:9000` (red interna), `STORAGE_PUBLIC_ENDPOINT=http://localhost:${STORAGE_HOST_PORT:-9000}` (base de las URL prefirmadas que abre el navegador), `STORAGE_BUCKET`, `STORAGE_ACCESS_KEY` y `STORAGE_SECRET_KEY` (obligatorios con `:?`).

### 3.3 Exposición

- La red `data` es interna y no permite publicar puertos (TK-001 §3.3); por eso `storage` se une también a `edge`.
- Solo se publica la API S3 en `127.0.0.1`. Como el *bucket* es privado, sin firma no se puede leer nada.
- En producción la URL pública es la del servicio S3 gestionado (README §2.4).

### 3.4 Retirada de `api_assets`

- Eliminar el volumen `api_assets`, su montaje y la variable `ASSETS_DIR` (servicio `api`, `Settings`, `Dockerfile` y documentación). La prueba de persistencia de TK-002 (AC3) deja de aplicar.

### 3.5 Makefile

- Sin targets nuevos: `make dev` levanta `storage` y `storage-init` como dependencias de `api`. `make clean` conserva `storage_data`.

### 3.6 Imagen, versión y licencia

- **Situación de MinIO:** MinIO, Inc. dejó de publicar imágenes Docker y binarios de la edición comunitaria en octubre de 2025, la puso en modo mantenimiento en diciembre de 2025 y archivó el repositorio en 2026. `minio/minio` y `minio/mc` ya no están disponibles en Docker Hub (`404`).
- **Imagen elegida:** `pgsty/minio`, compilación comunitaria mantenida (proyecto Silo, de Pigsty) a partir de la última versión de MinIO, sin cambios de API. No está afiliada a MinIO, Inc.
  - Servidor: `pgsty/minio:RELEASE.2026-08-04T00-00-00Z` (`minio --version` → `RELEASE.2026-08-04T00-00-00Z`, Go 1.26.5, base RHEL 9). Incluye `mc` y `curl`.
  - Cliente: el `mc` de la propia imagen. Si se necesita aparte, `pgsty/mc` con versión fija.
  - Siempre con etiqueta `RELEASE.…` fija, nunca `latest`; para actualizar, revisar las notas de la versión y repetir la verificación de la sección 6.
- **Licencia:** GNU AGPLv3 (servidor y cliente). EntreVecinos usa MinIO sin modificar, como servicio independiente al que la API accede por el protocolo S3, por lo que la AGPL no se extiende a su código. Si se modificara MinIO y se ofreciera como servicio en red, habría que publicar esas modificaciones.
- **Producción:** no aplica; se usa un servicio S3 gestionado (README §2.4). MinIO es solo para desarrollo local.
- **Alternativas** si la imagen dejara de mantenerse: compilar MinIO desde el código fuente o migrar a otro servidor compatible con S3 (p. ej. Garage, AGPLv3). La API solo depende del protocolo S3 (TK-021), así que el cambio queda en `infra/`.
- Documentarlo en `infra/README.md` (imagen, versión, licencia y procedimiento de actualización).

## 4. Criterios de aceptación

**AC1 — Arranque**
- **Given** un `.env` copiado de `.env.example`
- **When** ejecuto `make dev`
- **Then** `storage` queda `healthy`, `storage-init` termina con código 0 y `api` arranca después

**AC2 — Bucket privado y credenciales mínimas**
- **Given** el entorno levantado
- **When** intento leer un objeto sin firma (`curl http://localhost:9000/entrevecinos-media/x`) y uso las credenciales de la API para listar *buckets*
- **Then** la lectura anónima devuelve `403` y el listado de *buckets* está denegado; con las mismas credenciales sí puedo subir y leer un objeto del *bucket*

**AC3 — Idempotencia y persistencia**
- **Given** un objeto subido
- **When** ejecuto `make dev` de nuevo y recreo los contenedores sin `-v`
- **Then** `storage-init` termina sin errores y el objeto sigue existiendo

**AC4 — Sin exposición innecesaria**
- **Given** la configuración por defecto
- **When** reviso los puertos publicados
- **Then** solo `127.0.0.1:9000` está publicado para `storage` (la consola no) y no queda ninguna referencia a `api_assets` ni a `ASSETS_DIR`

## 5. Plan de tareas

1. Servicios `storage` y `storage-init`, volumen y variables.
2. `infra/storage/init.sh` y `api-policy.json`.
3. Retirada de `api_assets` y `ASSETS_DIR`.
4. `infra/README.md` (servicios, imagen, versión y licencia, depuración con la consola, borrado de datos).
5. Verificación según la sección 6.

## 6. Verificación

```bash
cp -n .env.example .env   # añadir las variables nuevas a un .env existente
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE ps -a storage storage-init                  # healthy / exited (0)
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:9000/entrevecinos-media/x   # 403
$COMPOSE run --rm --entrypoint sh storage-init -c \
  'mc alias set api http://storage:9000 "$STORAGE_ACCESS_KEY" "$STORAGE_SECRET_KEY" && mc ls api || true'
docker port entrevecinos-storage-1                   # solo 127.0.0.1:9000
grep -rn 'api_assets\|ASSETS_DIR' infra apps/api || echo "sin referencias"
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Ninguna credencial real en el repositorio; las de la API son distintas de las de administración de MinIO.
- [ ] `infra/README.md` documenta el servicio, la imagen, su versión y su licencia.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Host de las URL prefirmadas:** la firma incluye el host. La API debe firmar con `STORAGE_PUBLIC_ENDPOINT` (lo que ve el navegador) aunque suba por `STORAGE_ENDPOINT` (TK-021).
- **Imagen de MinIO no oficial:** depende de un mantenimiento comunitario (§3.6). Mitigación: versión fija, verificación al actualizar y alternativas documentadas.
- **Copias de seguridad de `storage_data`:** fuera de alcance en local; en producción las cubre el servicio gestionado.
