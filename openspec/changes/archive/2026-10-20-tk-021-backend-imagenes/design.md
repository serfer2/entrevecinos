## Context

TK-019 levantó MinIO con un bucket privado y credenciales de la API; TK-020 creó `media_asset` y `listing_image`. Contrato: `media.yaml`, `media_asset_id.yaml`, `MediaAsset`.

## Goals / Non-Goals

**Goals:** decidir el tipo solo por el contenido; no leer más de lo permitido; URL prefirmadas válidas para el navegador; regla de lectura en una consulta.

**Non-Goals:** `DELETE /media/{id}`, limpieza de huérfanos, miniaturas, EXIF.

## Decisions

- **Dos clientes `boto3`:** `STORAGE_ENDPOINT` (red interna) para subir y `STORAGE_PUBLIC_ENDPOINT` solo para firmar, porque la firma incluye el host que abrirá el navegador. Firmar no hace llamadas de red.
- **Lectura manual del multipart** (`request.form()`) en lugar de `UploadFile` como parámetro: permite rechazar por `Content-Length` antes de leer el cuerpo y leer como mucho `max + 1` bytes. El esquema de la petición se documenta con `openapi_extra`.
- **Clave `media/<uploaded_by>/<uuid4>.<ext>`**: nunca el nombre original.
- **Regla de lectura** (`MediaRepository.is_readable_by`): quien la subió, o un miembro aprobado de la comunidad de algún anuncio no eliminado que la use y que sea visible para él (`active`/`reserved`/`completed`, o `hidden` si es su autor o gestor de la comunidad). `platform_admin` puede leer cualquier imagen (asumido). TK-036 centralizará la visibilidad de anuncios.
- **El caso de uso se ejecuta en el *threadpool*** (`run_in_threadpool`) porque el endpoint es `async` para leer el formulario y el acceso a datos es síncrono.

## Risks / Trade-offs

- [Ficheros huérfanos si falla la base de datos tras subir] → se registra el error; limpieza periódica en un ticket posterior.
- [Sin `Content-Length` el cuerpo se guarda en un fichero temporal antes de cortar] → aceptable con el límite del servidor.
