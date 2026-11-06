# aws-ci-access Specification

## Purpose
Acceso de GitHub Actions a AWS sin OIDC (denegado por la política de control de servicios del proyecto): usuario IAM que solo asume un rol de despliegue de mínimo privilegio, con la clave solo en el entorno `production` de GitHub.
## Requirements
### Requirement: Rol de despliegue de mínimo privilegio
Terraform SHALL crear el rol `entrevecinos-github-deploy`, con sesión máxima de 1 hora, que MUST permitir solo: `ecr:GetAuthorizationToken`; subir imágenes a los repositorios `entrevecinos/api` y `entrevecinos/web`; `ssm:SendCommand` con el documento `entrevecinos-deploy` en la instancia de producción, y `ssm:GetCommandInvocation` y `ssm:ListCommandInvocations`. Las políticas MUST pasar IAM Access Analyzer sin avisos de seguridad.

#### Scenario: Acciones permitidas
- **WHEN** uso credenciales del rol para iniciar sesión en ECR y lanzar `entrevecinos-deploy` en la instancia
- **THEN** AWS lo permite

#### Scenario: Acciones denegadas
- **WHEN** uso credenciales del rol para leer un parámetro de `/entrevecinos/prod`, borrar una imagen de ECR o ejecutar `AWS-RunShellScript`
- **THEN** AWS responde `AccessDenied`

### Requirement: Identidad de GitHub sin permisos propios
Como la política de control de servicios del proyecto deniega los proveedores OIDC, Terraform SHALL crear el usuario IAM `entrevecinos-github-actions` cuyo único permiso MUST ser `sts:AssumeRole` sobre `entrevecinos-github-deploy`, y la confianza del rol MUST admitir solo a ese usuario con el `ExternalId` `entrevecinos-github-actions`. Su clave de acceso MUST NOT estar en el estado de Terraform ni en el repositorio.

#### Scenario: Clave sin permisos directos
- **WHEN** uso la clave del usuario sin asumir el rol para llamar a ECR o SSM
- **THEN** AWS responde `AccessDenied`

#### Scenario: Sin ExternalId
- **WHEN** el usuario intenta asumir el rol sin el `ExternalId`
- **THEN** AWS responde `AccessDenied`

### Requirement: Credenciales solo para main
La clave SHALL guardarse como secretos `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` del entorno `production` de GitHub, limitado a despliegues desde `main`; el ARN del rol, su `ExternalId` y la instancia MUST ser variables, no secretos. El repositorio MUST NOT tener claves de AWS como secretos del repositorio.

#### Scenario: Otra rama
- **WHEN** un *workflow* de otra rama o de un *fork* usa el entorno `production`
- **THEN** GitHub no le entrega los secretos y no puede asumir el rol

