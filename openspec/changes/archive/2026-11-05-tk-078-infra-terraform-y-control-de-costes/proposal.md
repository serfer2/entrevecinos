## Why

HU-36: producción en AWS necesita una base común de Terraform (estructura, estado remoto, proveedores, etiquetas y calidad) y, antes que nada, un gasto acotado a 40 €/mes con avisos, porque el proyecto vive de créditos y un recurso olvidado puede agotarlos. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-078-infra-terraform-y-control-de-costes.md`.

## What Changes

- Límite de gasto de 40 €/mes en AWS Settings (paso manual del propietario, documentado).
- `infra/aws/bootstrap/`: bucket del estado con versionado, cifrado, sin acceso público, solo TLS y `prevent_destroy`; módulo reutilizable `modules/private-bucket`.
- `infra/aws/envs/prod/`: *backend* S3 con `use_lockfile`, proveedor en `eu-north-1` y alias `us_east_1`, etiquetas por defecto, versiones fijadas y `.terraform.lock.hcl`.
- `modules/budget`: presupuesto mensual igual al límite, con avisos al 50/75/90 % real y 100 % previsto.
- `make tf-bootstrap|tf-init|tf-plan|tf-apply|tf-output|tf-lint` en contenedores; tflint y checkov con sus excepciones justificadas; `.gitignore` de Terraform.

## Capabilities

### New Capabilities
- `aws-foundation`: límite de gasto, presupuesto, estado remoto de Terraform y herramientas de calidad de la infraestructura.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/` (secciones «Estructura», «Puesta en marcha» y «Costes» de `infra/aws/README.md`), `Makefile`, `.gitignore`.
- Crea recursos en AWS: bucket del estado y presupuesto (coste ≈ 0).
