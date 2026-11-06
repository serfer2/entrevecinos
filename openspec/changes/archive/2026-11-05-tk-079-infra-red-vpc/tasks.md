## 1. Infraestructura

- [x] 1.1 Módulo `network`: VPC, subred pública, Internet Gateway, tabla de rutas y endpoint de S3
- [x] 1.2 Grupo por defecto sin reglas y grupo `entrevecinos-prod-app` con la *prefix list* de CloudFront
- [x] 1.3 *Flow logs* de tráfico rechazado con su rol y retención
- [x] 1.4 Composición en `envs/prod` y salidas

## 2. Aplicación en AWS

- [x] 2.1 `make tf-apply` y comprobación de grupos de seguridad y rutas (`aws ec2 describe-security-groups`, `describe-route-tables`)

## 3. Verificación

- [x] 3.1 `make tf-lint` sin errores
- [x] 3.2 Segundo `make tf-plan` sin cambios
