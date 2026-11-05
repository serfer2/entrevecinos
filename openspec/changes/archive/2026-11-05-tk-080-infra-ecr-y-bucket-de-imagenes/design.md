## Context

Las imágenes `prod` se publicarán desde el equipo (TK-086) y desde GitHub Actions (TK-090); la instancia las descargará con su rol (TK-085). La API firma las URL de las fotografías con la región y el estilo *virtual-hosted* (TK-081).

## Goals / Non-Goals

**Goals:** registro y bucket privados con valores seguros por defecto.

**Non-Goals:** permisos de lectura y escritura (TK-085, TK-088); CloudFront delante de las imágenes.

## Decisions

- **Etiquetas inmutables** en ECR: un *digest* por SHA de *commit*, imposible de sobrescribir.
- **Ciclo de vida de ECR:** sin etiqueta a los 7 días; como mucho 10 etiquetadas.
- **Sin CORS en el bucket:** el navegador carga las imágenes con `<img>`.
- **Origen público** como salida (`https://<bucket>.s3.eu-north-1.amazonaws.com`), para la CSP (`STORAGE_PUBLIC_URL`).

## Risks / Trade-offs

- [El ID de la cuenta aparece en las URL prefirmadas] → no es secreto; alternativa: sufijo aleatorio.
- [Escaneo básico de ECR, no Inspector] → coste; se revisa con la evolución.
