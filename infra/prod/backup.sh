#!/bin/bash
# Copia de PostgreSQL de producción (TK-082). La ejecuta cada 6 horas el temporizador
# entrevecinos-backup.timer, y a demanda antes de una migración destructiva.
#
# 1. pg_dump en formato personalizado (comprimido) como entrevecinos_owner.
# 2. Subida en streaming al bucket de copias con SSE-S3, sin dejar la copia en disco.
# 3. Comprobación: tamaño mínimo y `pg_restore --list` sobre la copia subida.
# 4. Métrica Entrevecinos/Backup BackupSucceeded = 1 (la alarma de TK-091 salta si falta).
#
# Configuración (no secreta) por entorno: BACKUP_BUCKET y AWS_REGION. La contraseña se lee de
# Parameter Store al ejecutarse y solo vive en el entorno de este proceso. Usa `docker`, no
# `docker compose`: el Compose de producción exige los secretos del despliegue (TK-086).
set -euo pipefail
set +x

: "${BACKUP_BUCKET:?Falta BACKUP_BUCKET}"
export AWS_REGION="${AWS_REGION:-eu-north-1}"
min_bytes="${BACKUP_MIN_BYTES:-1024}"

key="postgres/$(date -u +%Y/%m/%d)/$(date -u +%Y%m%dT%H%M%SZ).dump"
uri="s3://${BACKUP_BUCKET}/${key}"

PGPASSWORD="$(aws ssm get-parameter --name /entrevecinos/prod/db/owner-password \
  --with-decryption --query Parameter.Value --output text)"
export PGPASSWORD

container="$(docker ps -q --filter label=com.docker.compose.project=entrevecinos \
  --filter label=com.docker.compose.service=db)"
if [[ -z $container ]]; then
  echo "El contenedor db no está en marcha" >&2
  exit 1
fi

db() {
  docker exec -i -e PGPASSWORD "$container" "$@"
}

echo "Copia de PostgreSQL en ${uri}"
db pg_dump --format=custom --username=entrevecinos_owner --dbname=entrevecinos \
  | aws s3 cp - "$uri" --sse AES256 --only-show-errors

size="$(aws s3api head-object --bucket "$BACKUP_BUCKET" --key "$key" \
  --query ContentLength --output text)"
if (( size < min_bytes )); then
  echo "La copia ocupa ${size} bytes (mínimo ${min_bytes}): se considera fallida" >&2
  exit 1
fi

aws s3 cp "$uri" - --only-show-errors | db pg_restore --list >/dev/null

aws cloudwatch put-metric-data --namespace Entrevecinos/Backup \
  --metric-name BackupSucceeded --value 1 --unit Count
echo "Copia correcta: ${size} bytes"
