## Context

Sin alta disponibilidad mientras el proyecto no escale: una instancia en una zona (TK-085), PostgreSQL en la propia instancia (TK-082), CloudFront delante (TK-087).

## Goals / Non-Goals

**Goals:** exposición mínima de la instancia y sin NAT Gateway (≈ 35 USD/mes).

**Non-Goals:** la instancia (TK-085); subredes privadas (no hay recursos que las necesiten).

## Decisions

- **Una subred pública** en `availability_zone` (por defecto `eu-north-1a`); `10.20.1.0/24` reservado para una segunda zona.
- **Reglas con `aws_vpc_security_group_*_rule`** en lugar de bloques en línea: una regla por recurso y sin deriva.
- **Solo salida 443:** ECR, SSM, Parameter Store, SES, CloudWatch y S3; la hora (169.254.169.123) y el DNS de la VPC no pasan por el grupo de seguridad.
- **Grupo por defecto vaciado** (`aws_default_security_group` sin reglas).
- **Flow logs de tráfico rechazado** (no todo el tráfico) para limitar el coste.

## Risks / Trade-offs

- [La *prefix list* de CloudFront cuenta como ~55 reglas] → no se añaden más reglas de entrada a este grupo.
- [checkov marca el puerto 80 y el grupo sin adjuntar] → falso positivo (origen es la *prefix list*) y grupo que adjunta TK-085; excepciones en el recurso.
