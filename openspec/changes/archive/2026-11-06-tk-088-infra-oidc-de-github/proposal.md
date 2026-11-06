## Why

HU-37 AC3: el despliegue continuo (TK-090) necesita publicar imágenes en ECR y lanzar `entrevecinos-deploy` desde GitHub Actions con el mínimo privilegio y sin credenciales de administrador. El ticket prevé OIDC, pero la política de control de servicios del proyecto (plan FREE de AWS) deniega `iam:CreateOpenIDConnectProvider` e `iam:ListOpenIDConnectProviders`. Se aplica la alternativa del ticket, endurecida. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-37-publicar-nuevas-versiones-automaticamente-al-fusionar-en-main/TK-088-infra-oidc-de-github.md`.

## What Changes

- Módulo `infra/aws/modules/ci/` (nuevo):
  - Rol `entrevecinos-github-deploy` (sesión máxima de 1 hora) con permisos solo para subir imágenes a los dos repositorios de ECR y ejecutar `entrevecinos-deploy` en la instancia de producción, y seguir su resultado.
  - Usuario IAM `entrevecinos-github-actions` (ruta `/ci/`) cuyo único permiso es asumir ese rol con un `ExternalId`.
- La clave de acceso del usuario se crea con la AWS CLI (nunca en el estado de Terraform) y se guarda como secreto del entorno `production` de GitHub, que solo admite despliegues desde `main`; se rota cada 90 días.
- `envs/prod`: módulo `ci` y salidas (`github_user`, `github_deploy_role_arn`, `github_deploy_external_id`).
- Sin rol de solo lectura para `terraform plan` (opcional en el ticket): sería una segunda clave de larga duración al alcance de cualquier *pull request*; la validación de CI (`make tf-lint`) no necesita credenciales.

## Capabilities

### New Capabilities
- `aws-ci-access`: identidad de GitHub Actions en AWS, rol de despliegue de mínimo privilegio y gestión de su clave.

### Modified Capabilities
_(ninguna)_

## Impact

- Infraestructura: `infra/aws/modules/ci/`, `infra/aws/envs/prod/` e `infra/aws/README.md` («Puesta en marcha», «Despliegue continuo», «Secretos», «Operación» y «Decisiones de arquitectura»).
- Pasos manuales en GitHub: entorno `production` limitado a `main`, dos secretos y tres variables.
- Sin coste.
