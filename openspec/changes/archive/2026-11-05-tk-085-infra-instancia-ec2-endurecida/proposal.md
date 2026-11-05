## Why

HU-36: la web, la API y PostgreSQL corren con Docker Compose en una única instancia EC2 (por coste, mientras el proyecto no escale), así que su sistema operativo, su acceso remoto y sus permisos quedan a nuestro cargo (HU-36 AC3 y AC4). Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-085-infra-instancia-ec2-endurecida.md`.

## What Changes

- `modules/compute` (nuevo): instancia `t4g.small` con Amazon Linux 2023 arm64, IP pública y el grupo de seguridad de TK-079; sin par de claves ni SSH (`sshd` desactivado); IMDSv2 obligatorio con *hop limit* 2; créditos de CPU `standard` (sin cargos por exceso); volumen raíz cifrado de 20 GB; protección contra la terminación.
- Volumen de PostgreSQL (TK-082) adjunto y montado por UUID en `/srv/entrevecinos/postgres`, formateado solo si está vacío.
- *User data*: actualización, Docker con `live-restore` y logs rotados, Compose v5.6.1 con suma comprobada, agente de CloudWatch, `dnf-automatic` solo de seguridad, *swap* de 1 GB, usuario `deploy` sin *shell* y `/opt/entrevecinos` con permisos 750.
- Rol de instancia de mínimo privilegio (S3 de imágenes y copias, SES limitado al remitente, Parameter Store de `/entrevecinos/prod/`, ECR de lectura, métricas y logs propios) más `AmazonSSMManagedInstanceCore`.
- Session Manager con registro de sesiones en CloudWatch Logs; Patch Manager semanal; alarma de *status check* del sistema con acción `recover`.
- `infra/aws/README.md`: acceso a la instancia, parches, recuperación y coste.

## Capabilities

### New Capabilities
- `aws-compute`: instancia de aplicación endurecida, su rol y su operación (acceso, parches y recuperación).

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/compute/`, `infra/aws/modules/mail/` (salida de identidades de prueba), `infra/aws/envs/prod/` («Puesta en marcha», «Operación», «Costes» y «Decisiones de arquitectura» de `infra/aws/README.md`).
- Primer gasto real: ≈ 12 USD/mes de la instancia y 1,6 USD/mes del volumen raíz (la instancia entra en la capa gratuita del plan, cubierta por los créditos).
