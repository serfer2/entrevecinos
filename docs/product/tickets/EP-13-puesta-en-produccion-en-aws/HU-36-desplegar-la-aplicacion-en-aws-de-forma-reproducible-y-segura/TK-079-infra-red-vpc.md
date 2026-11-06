# TK-079 · Infraestructura: red (VPC, subredes y grupos de seguridad)

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/network/`, `infra/aws/envs/prod/` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-078 |
| **Referencias** | `readme.md` §2.2 («la base de datos y el almacenamiento deberían permanecer en una red interna»; en esta épica, la base de datos queda en la red interna de Compose, TK-082), §2.5 (aislamiento); *managed prefix list* `com.amazonaws.global.cloudfront.origin-facing` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El proyecto solo tiene la VPC por defecto, con todas sus subredes públicas. La arquitectura elegida es una única instancia EC2 con Docker Compose (proxy, web, API y PostgreSQL, TK-082) detrás de CloudFront, sin alta disponibilidad mientras el proyecto no escale. La instancia solo debe recibir tráfico de CloudFront; la base de datos no sale de la red interna de Compose.

**Objetivo:** una VPC propia y mínima, con una subred pública para la instancia, sin NAT Gateway (coste) y con un grupo de seguridad de mínimo privilegio.

## 2. Alcance

**Incluye**
- VPC `10.20.0.0/16` (asumido) con DNS habilitado.
- 1 subred pública (`10.20.0.0/24`) en una zona de disponibilidad (variable `availability_zone`, asumido: `eu-north-1a`); el volumen de datos de TK-082 se crea en la misma zona. Se reserva el rango `10.20.1.0/24` para una segunda zona cuando haga falta alta disponibilidad.
- Internet Gateway y tabla de rutas pública.
- Endpoint de VPC tipo *gateway* para S3 asociado a la tabla (gratuito; el tráfico a S3, incluidas las copias de TK-082, no sale a Internet).
- Grupos de seguridad:
  - `sg-app` (instancia): entrada TCP 80 solo desde la *prefix list* de CloudFront `origin-facing`; sin puerto 22 ni 5432; salida solo 443 a `0.0.0.0/0` (ECR, SSM y Parameter Store, SES, CloudWatch, S3) y 123/UDP para NTP si no se usa el servicio de hora de Amazon (asumido: se usa `169.254.169.123`, que no necesita regla).
- *Flow logs* de la VPC a CloudWatch Logs, solo tráfico rechazado y retención de 7 días (coste de céntimos al mes; asumido).
- La NACL por defecto se mantiene; la restricción se hace con los grupos de seguridad.

**No incluye**
- La instancia (TK-085) ni la base de datos (TK-082).
- Subredes privadas: no hay recursos que las necesiten mientras la base de datos esté en la instancia.
- NAT Gateway (≈ 35 USD/mes) ni endpoints de interfaz (≈ 7-8 USD/mes cada uno).

## 3. Requisitos técnicos

- La *prefix list* de CloudFront se obtiene con `data "aws_ec2_managed_prefix_list"` por nombre. Cuenta como ~55 reglas: comprobar la cuota «reglas por grupo de seguridad» (60 por defecto) y no añadir más reglas de entrada a `sg-app`.
- Salidas del módulo: IDs de VPC, de la subred, de su zona de disponibilidad y del grupo de seguridad.
- Etiquetas `Name` legibles (`entrevecinos-prod-public-a`…).

## 4. Criterios de aceptación

**AC1 — Sin puertos de base de datos (HU-36 AC3)**
- **Given** la red creada
- **When** reviso los grupos de seguridad de la VPC
- **Then** ninguno admite el puerto 5432 ni el 22 desde ningún origen

**AC2 — Instancia solo accesible desde CloudFront (HU-36 AC3)**
- **Given** `sg-app`
- **When** reviso sus reglas de entrada
- **Then** la única regla es TCP 80 desde la *prefix list* de CloudFront y no hay regla para el puerto 22

**AC3 — Tráfico a S3 privado**
- **Given** el endpoint *gateway* de S3
- **When** reviso la tabla de rutas
- **Then** tiene la ruta a la *prefix list* de S3 por el endpoint

**AC4 — Reproducible (HU-36 AC1)**
- **Given** el módulo aplicado
- **When** ejecuto de nuevo `terraform plan`
- **Then** no hay cambios

## 5. Plan de tareas

1. Módulo `network` con VPC, subredes, rutas e Internet Gateway.
2. Endpoint *gateway* de S3.
3. Grupos de seguridad y *prefix list* de CloudFront.
4. *Flow logs* y retención.
5. Composición en `envs/prod`, `plan` y `apply`.

## 6. Verificación

```bash
make tf-plan && make tf-apply
aws ec2 describe-security-groups --filters Name=tag:Project,Values=entrevecinos --profile entrevecinos \
  --query 'SecurityGroups[].{name:GroupName,in:IpPermissions}'
aws ec2 describe-route-tables --filters Name=tag:Project,Values=entrevecinos --profile entrevecinos
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `make tf-lint` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Una sola zona de disponibilidad:** si la zona cae, la web cae; aceptado mientras el proyecto no escale (sin alta disponibilidad). Añadir la segunda subred es un cambio menor de Terraform.
- **Instancia en subred pública sin NAT:** es el compromiso de coste elegido. La instancia tiene IP pública (≈ 3,6 USD/mes por IPv4), pero no acepta conexiones salvo de CloudFront. Alternativa más segura: instancia en subred privada con **orígenes VPC de CloudFront** (sin IP pública), que exige salida a Internet por NAT o endpoints de interfaz (+35 USD/mes o +40 USD/mes); se evalúa en TK-087.
- **IPv6:** podría eliminar el coste de la IPv4 pública, pero ECR, SSM y otros servicios no tienen *endpoints* IPv6 en todos los casos; se descarta en el MVP (asumido).
- **Dependencia de la prefix list:** si en el futuro hay que abrir otra regla de entrada, no cabrá en el mismo grupo; se usaría un segundo grupo de seguridad.
