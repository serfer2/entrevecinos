## Why

HU-36: la instancia de producción solo debe recibir tráfico de CloudFront y nada debe exponer la base de datos ni SSH (HU-36 AC3). El proyecto solo tiene la VPC por defecto. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-079-infra-red-vpc.md`.

## What Changes

- `modules/network`: VPC propia, una subred pública (sin IP pública por defecto), Internet Gateway, endpoint *gateway* de S3, grupo por defecto sin reglas y grupo `entrevecinos-prod-app` (entrada 80 solo desde la *prefix list* de CloudFront, salida 443).
- *Flow logs* del tráfico rechazado con retención de 7 días.

## Capabilities

### New Capabilities
- `aws-network`: red de producción mínima y grupo de seguridad de la instancia.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/network/`, `infra/aws/envs/prod/` («Estructura» de `infra/aws/README.md`).
- Crea recursos en AWS (coste ≈ 0; *flow logs* de céntimos).
