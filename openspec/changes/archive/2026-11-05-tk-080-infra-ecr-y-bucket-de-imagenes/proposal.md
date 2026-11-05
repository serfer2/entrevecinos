## Why

HU-36: producción necesita un registro privado para las imágenes `prod` de `api` y `web` y un bucket privado para las fotografías, que el navegador solo lee con URL prefirmadas (HU-36 AC3). Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-080-infra-ecr-y-bucket-de-imagenes.md`.

## What Changes

- `modules/storage`: repositorios ECR `entrevecinos/api` y `entrevecinos/web` (etiquetas inmutables, escaneo al subir, ciclo de vida).
- Bucket `entrevecinos-media-<cuenta>` con el módulo `private-bucket` (sin acceso público, SSE-S3, solo TLS, versionado y caducidad de versiones antiguas a los 30 días).
- Salidas: URL de los repositorios, bucket y origen de las URL prefirmadas para la CSP.

## Capabilities

### New Capabilities
- `aws-storage`: registro de imágenes Docker y bucket de fotografías de producción.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/storage/`, `infra/aws/envs/prod/` («Estructura» de `infra/aws/README.md`).
- Crea recursos en AWS (coste de céntimos).
