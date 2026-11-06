## 1. Comprobación

- [x] 1.1 Política de control de servicios: `iam:CreateOpenIDConnectProvider` denegado → alternativa del ticket (usuario que solo asume el rol)

## 2. Terraform

- [x] 2.1 Módulo `ci`: rol `entrevecinos-github-deploy` con su política, usuario `entrevecinos-github-actions` y confianza con `ExternalId`
- [x] 2.2 Módulo y salidas en `envs/prod`; `make tf-lint` sin errores
- [x] 2.3 `make tf-apply`

## 3. Documentación

- [x] 3.1 `infra/aws/README.md`: «Puesta en marcha», «Despliegue continuo» (clave, entorno de GitHub, rotación), «Secretos», «Operación» y «Decisiones de arquitectura»

## 4. Verificación

- [x] 4.1 IAM Access Analyzer sin avisos de seguridad en las dos políticas
- [x] 4.2 Prueba con una clave temporal: sin el rol y sin `ExternalId` se deniega; con el rol, ECR y `entrevecinos-deploy` se permiten y el resto se deniega (AC2, AC3); clave borrada al terminar
- [x] 4.3 Clave definitiva en el entorno `production` de GitHub (limitado a `main`) y variables (AC1); `make tf-plan` sin cambios
