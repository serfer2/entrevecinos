#!/bin/sh
# Inicializa MinIO (idempotente): bucket privado, usuario de la API y su política mínima.
# Lo ejecuta el servicio `storage-init`. La imagen solo trae sh y mc (sin grep ni sed).
set -eu

POLICY=entrevecinos-api

mc alias set local http://storage:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null

mc mb --ignore-existing "local/$STORAGE_BUCKET"
mc anonymous set none "local/$STORAGE_BUCKET" >/dev/null

cat > /tmp/api-policy.json <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::$STORAGE_BUCKET/*"]
    }
  ]
}
JSON
mc admin policy create local "$POLICY" /tmp/api-policy.json >/dev/null

# `user add` es idempotente (actualiza la clave si el usuario ya existe).
mc admin user add local "$STORAGE_ACCESS_KEY" "$STORAGE_SECRET_KEY" >/dev/null
# Solo se asigna si falta: `attach` falla cuando la política ya está asignada.
case "$(mc admin user info local "$STORAGE_ACCESS_KEY")" in
  *"PolicyName: $POLICY"*) ;;
  *) mc admin policy attach local "$POLICY" --user "$STORAGE_ACCESS_KEY" >/dev/null ;;
esac

echo "Almacenamiento listo: bucket $STORAGE_BUCKET, usuario $STORAGE_ACCESS_KEY ($POLICY)."
