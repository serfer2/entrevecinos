## Context

TK-001 creó las redes `data` (interna) y `edge`. TK-002 dejó `api_assets` y `ASSETS_DIR` como paso previo al almacenamiento de objetos.

## Goals / Non-Goals

**Goals:** MinIO reproducible con versión fija, bucket privado, credenciales de la API distintas de las de administración, inicialización idempotente.

**Non-Goals:** cliente S3 en la API (TK-021); almacenamiento de producción.

## Decisions

- **Imagen `pgsty/minio` con versión fija:** MinIO dejó de publicar imágenes oficiales (`minio/minio` ya no existe en Docker Hub). Licencia AGPLv3; se usa sin modificar como servicio aparte (TK-019 §3.6).
- **`storage-init` usa la misma imagen** (incluye `mc`) con `entrypoint: sh`, así solo hay una versión que fijar.
- **Script de inicialización solo con `sh` y `mc`:** la imagen no incluye `grep` ni `sed`; la política se genera con un *heredoc* (sustituye al `api-policy.json` previsto en el ticket, evitando duplicar el nombre del bucket) y el `attach` se salta si la política ya está asignada.
- **Política mínima** de la API: `s3:GetObject`, `s3:PutObject` y `s3:DeleteObject` sobre `arn:aws:s3:::<bucket>/*`; sin listar buckets.
- **Puerto S3 en `127.0.0.1`**, porque el navegador abre las URL prefirmadas; la consola (9001) solo con `docker-compose.storage-debug.yml`.

## Risks / Trade-offs

- [Imagen comunitaria] → versión fija, verificación al actualizar y alternativas documentadas en `infra/README.md`.
- [Quien tenga un `.env` antiguo] → debe añadir las variables nuevas; Compose falla con un mensaje claro (`:?`).
