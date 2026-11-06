## Why

HU-39 AC3 y AC4: las decisiones que separan producción de la arquitectura prevista en el `readme.md` estaban repartidas por los tickets y sin un resumen frente a lo previsto, y no había una hoja de ruta para cuando el proyecto escale. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-39-entender-las-decisiones-de-la-arquitectura-de-produccion-y-mantener-su-documentacion-al-dia/TK-095-docs-decisiones-de-arquitectura-y-evolucion.md`.

## What Changes

- `infra/aws/README.md`, «Decisiones de arquitectura»: introducción y tabla resumen por área (cómputo, base de datos, protección web, DNS, origen, red, secretos) con lo previsto, lo elegido, el coste evitado, el riesgo aceptado y el enlace a su entrada; entradas nuevas de red (TK-079), secretos (TK-083) y DNS (TK-084).
- `infra/aws/README.md`, «Evolución»: siete pasos en orden (RDS, Multi-AZ, ECS Fargate + ALB, WAF, DNSSEC, origen cifrado, orígenes VPC) con señal de disparo, coste y dependencias, y otras mejoras (OIDC, Object Lock, monitorización externa, *blue/green*).
- `readme.md` §2.4: «Diferencias con la arquitectura prevista», con el motivo de coste, una tabla resumida y enlaces a las dos secciones; sustituye al párrafo de la base de datos de TK-093.
- La protección web refleja lo desplegado (CloudFront sin WAF, TK-087), no el plan gratuito de CloudFront que suponía el ticket.

## Capabilities

### New Capabilities
- `architecture-decisions`: registro de decisiones frente a la arquitectura prevista y evolución recomendada.

### Modified Capabilities
- (ninguna)

## Impact

- Solo documentación: `infra/aws/README.md` («Decisiones de arquitectura» y «Evolución») y `readme.md` §2.4. Sin cambios de código ni de infraestructura.
