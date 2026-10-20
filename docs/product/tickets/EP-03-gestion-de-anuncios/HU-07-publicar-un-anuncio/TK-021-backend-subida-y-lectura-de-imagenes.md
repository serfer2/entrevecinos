# TK-021 · Backend: subida y lectura de imágenes (`POST /v1/media`, `GET /v1/media/{id}`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad y seguridad |
| **Componente** | `apps/api/` (área `media`, `infrastructure/storage/`) |
| **Historia** | HU-07 Publicar un anuncio (Épica 3) — fotografías |
| **Prioridad** | Alta |
| **Depende de** | TK-019, TK-020 |
| **Referencias** | `docs/api/paths/media.yaml`, `media_asset_id.yaml`; esquemas `MediaUpload`, `MediaAsset`; `readme.md` §2.5 (validación y control de acceso a imágenes) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Las fotografías se suben antes de asociarlas a un anuncio: `POST /media` devuelve un `id` y `GET /media/{id}` comprueba permisos y redirige a una URL prefirmada. El README exige validar los ficheros (JPEG, PNG o WebP, tamaño máximo) y los permisos de lectura.

**Objetivo:** implementar la subida y la lectura de imágenes sobre MinIO (TK-019), detrás de un puerto de almacenamiento.

## 2. Alcance

**Incluye**
- Puerto `ObjectStorage` (aplicación) y adaptador S3 con `boto3` (asumido: funciona igual con MinIO y con S3 gestionado).
- `POST /v1/media` (multipart) y `GET /v1/media/{id}` (302).
- Validación del tipo real por *magic bytes* y del tamaño.
- Regla de lectura según asociación a anuncios.

**No incluye**
- `DELETE /media/{id}` y limpieza de ficheros huérfanos (ver §8).
- Redimensionado o miniaturas (post-MVP).
- Avatares y perfiles profesionales (sin historia en el MVP).

## 3. Requisitos técnicos

### 3.1 Puerto y adaptador

```python
class ObjectStorage(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def presigned_get_url(self, key: str, expires_in: int) -> str: ...
```

- `S3ObjectStorage` usa **dos** clientes `boto3`: uno con `STORAGE_ENDPOINT` (interno) para subir, y otro con `STORAGE_PUBLIC_ENDPOINT` solo para firmar, porque la firma incluye el host que abrirá el navegador (TK-019 §8). Firmar no hace llamadas de red.
- Firma `SigV4`, `addressing_style="path"` (MinIO).
- Configuración (`Settings`): `storage_endpoint`, `storage_public_endpoint`, `storage_bucket`, `storage_access_key`, `storage_secret_key` (obligatorios), `media_max_bytes = 5_242_880`, `media_url_ttl_seconds = 300` (asumido).
- Dependencias: `boto3`; añadir `boto3` y `botocore` a las librerías prohibidas en `domain` y `application`.

### 3.2 `POST /v1/media` (autenticado, `multipart/form-data`, campo `file`)

1. Rechaza antes de leer todo el cuerpo si `Content-Length` supera `media_max_bytes` + margen del multipart; y, al leer, corta en `media_max_bytes + 1` bytes → **413** `{"detail": "La imagen supera el tamaño máximo de 5 MB."}`.
2. Detecta el tipo por *magic bytes* (JPEG `FF D8 FF`; PNG `89 50 4E 47 0D 0A 1A 0A`; WebP `RIFF????WEBP`), ignorando el `Content-Type` y la extensión enviados → si no es ninguno, **415** `{"detail": "Formato no permitido. Usa JPEG, PNG o WebP."}`. Fichero vacío → **422**.
3. Clave del objeto: `media/<uploaded_by>/<uuid4>.<ext>` (nunca el nombre original del fichero).
4. Calcula `sha256`, sube con el `Content-Type` detectado y guarda `media_asset`. Si falla la escritura en base de datos tras subir, se registra el error (el objeto huérfano se limpia según §8).
5. **201** `MediaAsset` (`id`, `url: "/v1/media/<id>"`, `mime_type`, `size_bytes`, `created_at`).

### 3.3 `GET /v1/media/{asset_id}` (autenticado)

- Puede leer la imagen:
  - quien la subió, o
  - un miembro aprobado de la comunidad de **algún** anuncio no eliminado que la use, siempre que el anuncio sea visible para él (no `hidden`, salvo su autor o un administrador o moderador de la comunidad; reglas de TK-036).
- **302** con `Location: <URL prefirmada>` (válida `media_url_ttl_seconds`) y `Cache-Control: private, max-age=<ttl - 30>` (asumido).
- **404** si no existe; **403** si existe pero no se puede leer (contrato).

### 3.4 Diseño por capas

- `domain/media/`: `MediaAsset`, `ImageType` (enum con `mime_type` y extensión), `detect_image_type(header: bytes) -> ImageType | None`, errores `UnsupportedImageType`, `ImageTooLarge`.
- `application/media/`: `UploadImage`, `GetImageUrl`; puertos `MediaRepository` (`add`, `get`, `is_readable_by(asset_id, user_id)`) y `ObjectStorage`.
- La regla de lectura se resuelve en una consulta del repositorio (`EXISTS` sobre `listing_image` + `listings` + `community_membership`).

### 3.5 Pruebas

- Unitarias: `detect_image_type` con cabeceras válidas, truncadas y falsas (un `.png` que es un PDF); casos de uso con `ObjectStorage` falso.
- Integración: subida JPEG/PNG/WebP (**201**), GIF o texto renombrado (**415**), 5 MB + 1 byte (**413**), sin token (**401**); lectura por el autor (**302** con URL del host público), por un miembro de la comunidad del anuncio (**302**), por un ajeno (**403**).
- Una prueba de extremo a extremo contra MinIO real (`@pytest.mark.storage`) que sube y descarga desde la URL prefirmada.

## 4. Criterios de aceptación

**AC1 — Subida correcta**
- **Given** que he iniciado sesión
- **When** subo un JPEG de 1 MB
- **Then** recibo `201` con `mime_type: "image/jpeg"` y `url: "/v1/media/<id>"`; el objeto existe en el *bucket* con una clave que no contiene el nombre original

**AC2 — Formato y tamaño**
- **Given** que he iniciado sesión
- **When** subo un PDF renombrado a `.jpg` o un PNG de más de 5 MB
- **Then** recibo `415` o `413` respectivamente, y no se guarda nada

**AC3 — Lectura con permiso**
- **Given** una imagen asociada a un anuncio de mi comunidad
- **When** llamo a `GET /v1/media/<id>`
- **Then** recibo `302` a una URL de `localhost:9000` que descarga la imagen durante 5 minutos y después caduca

**AC4 — Lectura sin permiso**
- **Given** una imagen de un anuncio de una comunidad a la que no pertenezco
- **When** llamo a `GET /v1/media/<id>`
- **Then** recibo `403`

## 5. Plan de tareas

1. Dependencia `boto3`, configuración y adaptador `S3ObjectStorage`.
2. Dominio (`detect_image_type`) y casos de uso con pruebas unitarias.
3. Repositorio (`media_asset`, regla de lectura).
4. Endpoints con límites de tamaño.
5. Pruebas de integración y de MinIO real; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s -X POST http://localhost:8000/v1/media -H "Authorization: Bearer $TOKEN" -F file=@foto.jpg     # 201
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/v1/media \
  -H "Authorization: Bearer $TOKEN" -F file=@documento.pdf;type=image/jpeg                          # 415
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:8000/v1/media/<id> \
  -H "Authorization: Bearer $TOKEN"                                                                # 302 http://localhost:9000/...
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] El tipo se decide solo por el contenido del fichero.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Ficheros huérfanos** (subidos y nunca asociados, o tras fallos): se propone una tarea periódica posterior que borre los no asociados con más de 24 h.
- **Metadatos EXIF** (ubicación de la foto): no se eliminan en el MVP; conviene reprocesar las imágenes (Pillow) en un ticket posterior.
- **Límite de subidas por usuario:** sin cuota ni limitación de peticiones.
