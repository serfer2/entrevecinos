## Context

Primer ticket de infraestructura de la Épica 13. El proyecto de AWS es `995006761619` (`eu-north-1`), plan gratuito con créditos; la sesión es de `aws login` (temporal).

## Goals / Non-Goals

**Goals:** base de Terraform para que el resto de tickets solo añadan módulos; gasto limitado y avisado.

**Non-Goals:** Terraform en CI (TK-089); recursos de la aplicación (TK-079 en adelante).

## Decisions

- **Herramientas en contenedores fijados por versión** (Terraform 1.16.7, tflint 0.65.0 con el *ruleset* de AWS 0.49.0, checkov 3.3.30), todas publicadas hace al menos dos semanas; proveedor `aws ~> 6.70.0` por el mismo motivo.
- **Credenciales por entorno:** `aws configure export-credentials` en una sustitución de proceso de bash pasada como `--env-file`; nada se escribe en disco y funciona con la sesión de `aws login` sin depender de que el SDK de Terraform la entienda.
- **`use_lockfile`** en el *backend* S3 en lugar de una tabla de DynamoDB.
- **Módulo `private-bucket`** compartido por el estado, las imágenes (TK-080) y las copias (TK-082), con `prevent_destroy`.
- **Presupuesto igual al límite** (44 USD, el equivalente de 40 € que muestra AWS Settings) con avisos al 50/75/90 %: el presupuesto avisa, el límite frena.
- **Excepciones de checkov** en `.checkov.yaml` (decisiones de coste: claves KMS propias, réplica entre regiones, registro de accesos, notificaciones de S3, retención de un año) y puntuales con `#checkov:skip`.

## Risks / Trade-offs

- [El estado del *bootstrap* es local] → se conserva fuera del repositorio; recrearlo solo exige importar el bucket.
- [El límite de gasto puede pausar producción] → avisos al 50/75/90 % y estimación de ≈ 20 USD/mes.
