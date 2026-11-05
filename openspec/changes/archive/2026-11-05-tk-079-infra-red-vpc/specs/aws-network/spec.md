## ADDED Requirements

### Requirement: Red mínima de producción
Terraform SHALL crear una VPC propia con una subred pública en una zona de disponibilidad, Internet Gateway y endpoint *gateway* de S3, sin NAT Gateway ni subredes privadas, y el grupo de seguridad por defecto MUST quedar sin reglas.

#### Scenario: Tráfico a S3
- **WHEN** reviso la tabla de rutas de la subred
- **THEN** tiene la ruta a Internet y la del endpoint de S3

### Requirement: Grupo de seguridad de la aplicación
El grupo `entrevecinos-prod-app` SHALL admitir entrada solo por TCP 80 desde la *prefix list* `com.amazonaws.global.cloudfront.origin-facing` y salida solo por TCP 443; ningún grupo de la VPC MUST admitir los puertos 22 o 5432.

#### Scenario: Sin SSH ni base de datos
- **WHEN** reviso los grupos de seguridad de la VPC
- **THEN** la única entrada es TCP 80 desde CloudFront y no hay reglas para 22 ni 5432

### Requirement: Registro del tráfico rechazado
La VPC SHALL registrar el tráfico rechazado en CloudWatch Logs (`/entrevecinos/prod/vpc-flow-logs`) con retención de 7 días.

#### Scenario: Flow logs
- **WHEN** consulto los *flow logs* de la VPC
- **THEN** están activos con `REJECT` hacia ese grupo de registros
