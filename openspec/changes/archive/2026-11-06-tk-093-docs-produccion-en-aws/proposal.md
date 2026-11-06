## Why

HU-38 AC4: `readme.md` §2.4 describía una producción genérica (CDN con WAF, balanceador, contenedores y base de datos gestionados) y terminaba en «Pendiente», y a `infra/aws/README.md` le faltaban el *runbook*, la estimación de costes y cómo destruir el entorno. Cualquier persona del proyecto debe poder crear, desplegar, operar y destruir producción siguiendo la guía. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-38-vigilar-recuperar-y-operar-produccion/TK-093-docs-produccion-en-aws.md`.

## What Changes

- `readme.md`:
  - §2.4: diagramas de desarrollo local y de la producción real (Route 53, CloudFront sin WAF, instancia EC2 con proxy, web, API y PostgreSQL, S3, SES, Parameter Store, CloudWatch y SNS; GitHub Actions, ECR y SSM), texto de producción, decisión de PostgreSQL en la instancia sin alta disponibilidad **para ahorrar costes mientras el proyecto no escale** con sus mitigaciones, integración y despliegue continuos, diferencias técnicas; sin la nota «Pendiente»;
  - §2.5: medidas de seguridad reales;
  - §2.2: el correo de producción va por SES.
- `infra/aws/README.md`: variables y salidas en «Puesta en marcha»; «Runbook» (sesión de AWS y `AccessDenied`, `platform_admin`, desplegar un commit, rotar secretos, actualizar PostgreSQL menor y mayor, migrar a RDS, reemplazar la instancia); costes con el gasto real y la estimación por servicio; «Destruir el entorno».
- `infra/README.md`: enlaces al Compose y los scripts de producción.
- `AGENTS.md`: rutas de producción, comandos `make tf-*` y la regla de no aplicar, destruir ni desplegar sin confirmación.
- `.env.example`: bloque comentado con las variables de producción (valores ficticios).

## Capabilities

### New Capabilities
- `production-documentation`: documentación de la producción real en `readme.md` y guía completa (*runbook*, costes y destrucción) en `infra/aws/README.md`.

### Modified Capabilities
- (ninguna)

## Impact

- Solo documentación: `readme.md`, `infra/aws/README.md`, `infra/README.md`, `AGENTS.md`, `.env.example`. Toca `infra/aws/README.md` (rutas de infraestructura): «Puesta en marcha», «Operación» («Runbook»), «Costes» y «Destruir el entorno».
- Sin cambios de código, de la API, del contrato, de la infraestructura ni migraciones.
