# TK-080 · Infraestructura: repositorios ECR y bucket S3 de imágenes

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/storage/`, `infra/aws/envs/prod/` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-078 |
| **Referencias** | `AGENTS.md` («las imágenes se leen siempre con URL prefirmada, nunca con un bucket público»); TK-019 (MinIO), TK-021 (subida y lectura), TK-046 (CSP `img-src`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

En local las imágenes de los anuncios viven en MinIO y las imágenes Docker se construyen en el equipo. En producción hace falta un registro privado para las imágenes `prod` de `api` y `web`, y un bucket S3 privado para las fotografías, que el navegador lee solo con URL prefirmadas por la API (redirección `302` desde `/media/<id>`).

**Objetivo:** crear los repositorios ECR y el bucket de imágenes con configuración segura por defecto.

## 2. Alcance

**Incluye**
- ECR: repositorios `entrevecinos/api` y `entrevecinos/web`:
  - etiquetas inmutables (`IMMUTABLE`), escaneo al subir (*basic scanning*), cifrado AES-256;
  - política de ciclo de vida: conservar las 10 últimas imágenes etiquetadas y borrar las no etiquetadas a los 7 días.
- S3: bucket `entrevecinos-media-995006761619`:
  - Block Public Access (las cuatro opciones), `BucketOwnerEnforced`, cifrado SSE-S3;
  - política que deniega `aws:SecureTransport = false`;
  - versionado con caducidad de versiones no actuales a los 30 días (recuperación ante borrados accidentales, TK-092);
  - regla de ciclo de vida que aborta subidas *multipart* incompletas a los 7 días.
- Salidas: URL de los repositorios, nombre y ARN del bucket, origen público para la CSP (`https://entrevecinos-media-995006761619.s3.eu-north-1.amazonaws.com`).

**No incluye**
- Permisos de lectura y escritura (rol de la instancia, TK-085; rol de CI, TK-088).
- Migración de imágenes existentes de MinIO (asumido: producción empieza vacía).
- CloudFront delante de las imágenes (ver §8).

## 3. Requisitos técnicos

- No se configura CORS en el bucket: el navegador carga las imágenes con `<img>`, que no necesita CORS (asumido; revisar si alguna vista las lee con `fetch`).
- El bucket no tiene política que conceda acceso a `*`; el acceso será exclusivamente por IAM.
- `force_destroy = false` y `prevent_destroy` en el bucket: borrar las fotografías debe ser una decisión explícita.

## 4. Criterios de aceptación

**AC1 — Bucket privado (HU-36 AC3)**
- **Given** el bucket creado
- **When** pido un objeto sin firmar (`curl https://<bucket>.s3.eu-north-1.amazonaws.com/<clave>`)
- **Then** recibo `403`

**AC2 — Solo TLS**
- **Given** la política del bucket
- **When** hago una petición por HTTP
- **Then** se deniega

**AC3 — Registro seguro**
- **Given** los repositorios ECR
- **When** subo una imagen con una etiqueta ya existente
- **Then** se rechaza, y cada imagen subida tiene un resultado de escaneo

**AC4 — Reproducible (HU-36 AC1)**
- **Given** el módulo aplicado
- **When** ejecuto de nuevo `terraform plan`
- **Then** no hay cambios

## 5. Plan de tareas

1. Repositorios ECR y política de ciclo de vida.
2. Bucket, Block Public Access, cifrado, política TLS, versionado y ciclo de vida.
3. Salidas y composición en `envs/prod`.

## 6. Verificación

```bash
make tf-apply
aws s3api get-public-access-block --bucket entrevecinos-media-995006761619 --profile entrevecinos
aws ecr describe-repositories --profile entrevecinos \
  --query 'repositories[].{n:repositoryName,mut:imageTagMutability,scan:imageScanningConfiguration}'
curl -sI https://entrevecinos-media-995006761619.s3.eu-north-1.amazonaws.com/test | head -1   # 403
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `make tf-lint` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Servir las imágenes por CloudFront:** CloudFront con OAC delante del bucket daría caché y un único origen para la CSP, pero las URL prefirmadas de S3 no valen para CloudFront (habría que usar URL firmadas de CloudFront con un par de claves). Se descarta en el MVP: más piezas y secretos por poco beneficio con poco tráfico.
- **Escaneo mejorado (Inspector):** detecta vulnerabilidades del SO y de los paquetes, pero tiene coste y puede no estar en el plan gratuito; se usa el escaneo básico.
- **Nombre con el ID de la cuenta:** garantiza unicidad global; el ID de la cuenta no es secreto, pero queda visible en las URL prefirmadas. Alternativa: sufijo aleatorio.
