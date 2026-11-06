## Context

El entorno `production` de GitHub (limitado a `main`) tiene la clave del usuario de CI y las variables del rol, la región y la instancia (TK-088). El rol solo puede subir imágenes a los dos repositorios, ejecutar `entrevecinos-deploy` en la instancia y leer el resultado. `ci.yml` admite `workflow_call` (TK-089). Las etiquetas de ECR son inmutables (TK-080).

## Goals / Non-Goals

**Goals:** fusión en `main` → producción sin pasos manuales; fallo visible si `deploy.sh` vuelve atrás; un despliegue cada vez; redespliegue de un commit anterior de `main`.

**Non-Goals:** Terraform desde CI; *previews* por *pull request*; aprobación manual (opcional en el entorno).

## Decisions

- **Credenciales: clave del usuario de CI + rol, no OIDC** (TK-088). `configure-aws-credentials` asume el rol con `ExternalId` y sin etiquetas de sesión; las credenciales del rol duran 1 hora. Solo los trabajos `publish` y `deploy` usan el entorno `production` (y sus secretos); `checks` y `smoke` no.
- **Sin variables nuevas.** El ticket pedía `ECR_REGISTRY` y `PUBLIC_URL`: el registro se deduce de la cuenta del ARN del rol y la región; la URL pública va en el propio *workflow* (no es configuración que cambie).
- **`publish` en `ubuntu-24.04-arm`** con `build-push-action` y la caché `gha` de CI (solo lectura). Etiqueta: los 12 primeros caracteres del SHA, como el despliegue manual. Antes de construir, `ecr:BatchGetImage` (ya permitido) mira si la etiqueta existe: si sí, reutiliza su *digest* (reejecuciones y redespliegues de un commit anterior). `provenance: false` para que el *digest* sea el del manifiesto de `arm64`, el que valida el documento. `docker logout` al final.
- **`workflow_dispatch` con `sha` opcional**: solo commits que son ancestros de `origin/main` (`git merge-base --is-ancestor`), para que nadie despliegue un commit sin revisar. Con `sha`, se omite `checks` (ya pasó al fusionarse).
- **`deploy` con espera propia** (sondeo de `get-command-invocation` cada 10 s, hasta 20 min) en lugar de `aws ssm wait command-executed`, que se rinde a los 100 s y un despliegue tarda 2-4 min. Muestra la salida de `deploy.sh` (sin secretos, TK-086) y falla si el estado no es `Success`; con la vuelta atrás, `deploy.sh` termina con error y producción sigue con los *digests* anteriores.
- **Concurrencia a nivel de *workflow*** (`group: production`, sin cancelar): la segunda fusión espera completa a la primera. GitHub solo deja una ejecución pendiente por grupo: si llegan varias, se despliega la más reciente (que incluye las anteriores).
- **`ci.yml` sin `push` a `main`**: `deploy.yml` ya lo ejecuta; evita duplicar trabajo y minutos. Su `concurrency` solo cancela en *pull requests*.
- **`smoke`**: `/` con `200`/`307`/`308`, `/iniciar-sesion` con `200` y `Strict-Transport-Security` (detecta un despliegue sin la configuración de producción), 12 intentos cada 10 s.

## Risks / Trade-offs

- [Construcción duplicada: `checks` construye las imágenes sin publicar y `publish` otra vez] → la caché `gha` lo reduce; la alternativa (publicar desde `ci.yml`) mezclaría permisos.
- [Las migraciones no se deshacen en la vuelta atrás] → *expand/contract* (TK-086, TK-093).
- [Un *smoke test* fallido no vuelve atrás] → `deploy.sh` ya comprueba salud y origen; el fallo del *smoke* indica un problema de CloudFront o DNS, no de la versión.
- [Aprobación manual desactivada] → activable en el entorno (*Required reviewers*) si hay más personas con escritura.
