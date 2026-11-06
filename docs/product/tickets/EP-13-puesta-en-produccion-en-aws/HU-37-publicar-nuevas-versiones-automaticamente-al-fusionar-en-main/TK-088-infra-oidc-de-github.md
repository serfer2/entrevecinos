# TK-088 · Infraestructura: acceso de GitHub Actions a AWS con OIDC

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/ci/`, `infra/aws/envs/prod/` |
| **Historia** | HU-37 Publicar nuevas versiones automáticamente al fusionar en `main` (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-080, TK-085 |
| **Referencias** | Documentación de GitHub «Configuring OpenID Connect in Amazon Web Services»; `aws-actions/configure-aws-credentials` |

> **Implementado sin OIDC.** La política de control de servicios del plan FREE de AWS deniega `iam:CreateOpenIDConnectProvider`. GitHub Actions usa la clave de un usuario IAM que solo puede asumir, con un identificador externo, el rol de despliegue de mínimo privilegio; la clave vive en el entorno `production` de GitHub, limitado a `main`. Decisión y evolución a OIDC: `infra/aws/README.md`, «Usuario IAM para GitHub Actions en lugar de OIDC (TK-088)».

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El despliegue continuo (TK-090) necesita publicar imágenes en ECR y ordenar el despliegue en la instancia. Guardar claves de acceso de AWS en GitHub es un riesgo (fuga, sin caducidad). Con OIDC, GitHub emite un token por ejecución que AWS cambia por credenciales temporales de un rol, solo si el token procede del repositorio y la rama esperados.

**Objetivo:** un proveedor OIDC de GitHub y un rol de despliegue de mínimo privilegio que solo puede asumirse desde `main` del repositorio `serfer2/entrevecinos`.

## 2. Alcance

**Incluye**
- `aws_iam_openid_connect_provider` para `https://token.actions.githubusercontent.com` con audiencia `sts.amazonaws.com`.
- Rol `entrevecinos-github-deploy`:
  - confianza: `sts:AssumeRoleWithWebIdentity` con condiciones `token.actions.githubusercontent.com:aud = sts.amazonaws.com` y `token.actions.githubusercontent.com:sub = repo:serfer2/entrevecinos:environment:production` (asumido: el *workflow* usa el entorno `production` de GitHub, TK-090);
  - duración máxima de la sesión: 1 hora.
- Permisos del rol:
  - `ecr:GetAuthorizationToken`; subida de imágenes (`ecr:BatchCheckLayerAvailability`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`, `ecr:BatchGetImage`) solo en los dos repositorios;
  - `ssm:SendCommand` solo con el documento `entrevecinos-deploy` y la instancia de producción (condición por ARN de instancia o etiqueta); `ssm:GetCommandInvocation` y `ssm:ListCommandInvocations` para seguir el resultado.
- Rol opcional de solo lectura `entrevecinos-github-plan` (asumido: para `terraform plan` en *pull requests*, TK-089), con `ReadOnlyAccess` y lectura del bucket de estado; confianza limitada a `repo:serfer2/entrevecinos:pull_request`.
- Salidas: ARN de los roles (se configuran como variables, no secretos, del repositorio en GitHub).

**No incluye**
- Los *workflows* (TK-089, TK-090).
- `terraform apply` desde CI (ver §8).

## 3. Requisitos técnicos

- Comprobar antes de implementar que el SCP gestionado del plan del proyecto permite `iam:CreateOpenIDConnectProvider` (hay indicios no verificados de que podría denegarse). Si no se permite, ver §8.
- La huella del certificado (*thumbprint*) ya no es necesaria para GitHub en AWS; si el proveedor de Terraform la exige, usar el valor documentado por GitHub.
- Validar las políticas con IAM Access Analyzer.
- Nada de `*` en `Resource`, salvo `ecr:GetAuthorizationToken`.

## 4. Criterios de aceptación

**AC1 — Sin credenciales guardadas (HU-37 AC3)**
- **Given** la configuración del repositorio en GitHub
- **When** reviso secretos y variables
- **Then** no hay claves de acceso de AWS; solo el ARN del rol como variable

**AC2 — Confianza limitada (HU-37 AC3)**
- **Given** un *workflow* de otra rama, de un *fork* o sin el entorno `production`
- **When** intenta asumir el rol de despliegue
- **Then** AWS lo rechaza con `AccessDenied`

**AC3 — Mínimo privilegio**
- **Given** credenciales del rol de despliegue
- **When** intento leer un secreto, borrar una imagen o ejecutar otro documento de SSM
- **Then** se deniega, y la subida a ECR y `entrevecinos-deploy` sí funcionan

## 5. Plan de tareas

1. Comprobación del SCP (`iam:CreateOpenIDConnectProvider`).
2. Proveedor OIDC y rol de despliegue con su política.
3. Rol de solo lectura para `plan` (opcional).
4. Validación con Access Analyzer y prueba desde un *workflow* mínimo.

## 6. Verificación

```bash
make tf-apply
aws iam get-role --role-name entrevecinos-github-deploy --profile entrevecinos --query 'Role.AssumeRolePolicyDocument'
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://<política>.json --profile entrevecinos
# Workflow de prueba en una rama: debe fallar al asumir el rol
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Políticas validadas sin avisos de seguridad.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **SCP del plan que deniega OIDC:** alternativa menos segura: un usuario IAM con clave de acceso (solo uso programático) y los mismos permisos mínimos, guardada como secreto de GitHub en el entorno `production` y rotada cada 90 días. Otra opción: activar las funciones avanzadas de la cuenta.
- **`terraform apply` desde CI:** exigiría un rol con permisos casi de administrador asumible desde GitHub. En el MVP la infraestructura se aplica a mano con `aws login`; el CI solo valida (y opcionalmente hace `plan`).
- ***Sub* por entorno o por rama:** limitar a `environment:production` permite exigir aprobación manual y reglas de protección en GitHub; limitar a `ref:refs/heads/main` es más simple. Se elige el entorno.
