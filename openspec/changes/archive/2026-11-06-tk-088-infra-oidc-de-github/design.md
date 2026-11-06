## Context

El estado de producción ya tiene los repositorios ECR (TK-080), la instancia (TK-085) y el documento `entrevecinos-deploy` (TK-086). `iam:CreateOpenIDConnectProvider` da `explicitDeny` en la política de control de servicios gestionada del proyecto (simulación con `iam simulate-principal-policy` y `AccessDenied` real en `ListOpenIDConnectProviders`). `iam:CreateUser`, `iam:CreateAccessKey`, `iam:CreateRole` y `sts:AssumeRole` sí se permiten.

## Goals / Non-Goals

**Goals:** que GitHub Actions pueda publicar imágenes y desplegar, con el mínimo privilegio, sin claves de administrador y con la clave fuera del estado y del repositorio.

**Non-Goals:** los *workflows* (TK-089, TK-090); `terraform apply` o `plan` desde CI; activar las funciones avanzadas de la cuenta.

## Decisions

- **Usuario que solo asume un rol, en lugar de un usuario con los permisos.** La clave de larga duración no da ningún permiso por sí misma: cada ejecución pide credenciales temporales del rol (1 hora como máximo), que quedan en CloudTrail como sesiones del rol. Pasar a OIDC cuando el plan lo permita solo cambia la confianza del rol y borra el usuario. Alternativa descartada: el usuario con la política del rol (más simple, pero la clave lleva los permisos y no hay sesiones).
- **`ExternalId` en la confianza** (`entrevecinos-github-actions`, no secreto): evita que el usuario asuma el rol por accidente sin intención explícita; la protección real es la clave.
- **Clave fuera de Terraform.** `aws_iam_access_key` guardaría el secreto en el estado. Se crea con `aws iam create-access-key` y se pasa a `gh secret set` por la entrada estándar, sin mostrarla ni escribirla en disco. Rotación cada 90 días: crear la nueva, actualizar los secretos, borrar la antigua (dos claves como máximo).
- **Restricción de rama en GitHub, no en AWS.** Sin OIDC, AWS no sabe de qué rama viene la petición. Los secretos van en el entorno `production`, con regla de despliegue solo desde `main`: otras ramas no reciben los secretos y los *forks* nunca los reciben. Opcional: revisores obligatorios.
- **Permisos del rol:** `ecr:GetAuthorizationToken` (no admite recursos); subida (`BatchCheckLayerAvailability`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload`, `PutImage`, `BatchGetImage`) solo en `entrevecinos/api` y `entrevecinos/web`; `ssm:SendCommand` solo en el documento `entrevecinos-deploy` y el ARN de la instancia; `ssm:GetCommandInvocation` y `ssm:ListCommandInvocations` con `*`, porque no admiten recursos concretos (solo leen el resultado; la salida del despliegue no tiene secretos, TK-086). Sin `ecr:BatchDeleteImage`, sin Parameter Store, sin otros documentos.
- **Sin rol de `plan`** (opcional en el ticket): sería otra clave de larga duración disponible para las ramas de *pull request*.

## Risks / Trade-offs

- [Clave de larga duración en GitHub] → solo asume el rol, vive en un entorno limitado a `main`, se rota cada 90 días y su uso queda en CloudTrail; si se filtra, se desactiva con `aws iam update-access-key --status Inactive`.
- [Un *workflow* malicioso fusionado en `main` puede desplegar] → revisión obligatoria de *pull requests* (TK-089) y, opcional, revisores del entorno.
- [`GetCommandInvocation` con `*`] → solo lectura de resultados de Run Command de la cuenta.
