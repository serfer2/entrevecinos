## Why

HU-37 AC2 a AC4: tras TK-086 a TK-089 se puede desplegar a mano y cada *pull request* se comprueba, pero llegar a producción sigue exigiendo construir, subir y lanzar el documento de SSM desde el equipo. Cada fusión en `main` debe llegar a producción sola, con vuelta atrás visible y sin dos despliegues a la vez. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-37-publicar-nuevas-versiones-automaticamente-al-fusionar-en-main/TK-090-ci-despliegue-continuo.md`.

## What Changes

- `.github/workflows/deploy.yml` (nuevo), en cada `push` a `main` y con `workflow_dispatch` (último commit de `main` o uno anterior de `main`):
  - `checks`: reutiliza `ci.yml`;
  - `publish` (entorno `production`): asume `entrevecinos-github-deploy` con la clave del usuario de CI (TK-088, sin OIDC), construye `api` y `web` (`prod`, `linux/arm64`, *runner* arm64), las sube a ECR con la etiqueta del commit (o reutiliza las que ya existen) y obtiene los *digests*;
  - `deploy` (entorno `production`): `entrevecinos-deploy` por SSM, espera el resultado, muestra la salida de `deploy.sh` y falla si no es `Success` (vuelta atrás incluida);
  - `smoke`: `/` y `/iniciar-sesion` por HTTPS con `Strict-Transport-Security`, con reintentos 2 minutos;
  - `concurrency: production` sin cancelación; resumen con commit, *digests* y resultado.
- `ci.yml`: deja de ejecutarse en `push` a `main` (lo hace `deploy.yml`, sin duplicar) y no cancela ejecuciones llamadas desde el despliegue.
- `infra/aws/README.md`: «Despliegue continuo», «Integración continua», «Despliegue manual» (pasa a ser la alternativa) y «Decisiones».

## Capabilities

### New Capabilities
- `continuous-deployment`: publicación de imágenes, despliegue por SSM, *smoke test* y concurrencia en cada fusión a `main`.

### Modified Capabilities
- `ci-checks`: `CI` se ejecuta en *pull requests* y como `workflow_call`; en `main`, desde el despliegue.

## Impact

- Nuevo `.github/workflows/deploy.yml`; cambiados `.github/workflows/ci.yml` e `infra/aws/README.md`.
- Sin cambios en AWS: usa el rol y las variables de TK-088 (`AWS_REGION`, `AWS_DEPLOY_ROLE_ARN`, `AWS_DEPLOY_ROLE_EXTERNAL_ID`, `DEPLOY_INSTANCE_ID`) y los secretos del entorno `production`.
- La fusión de este cambio en `main` es el primer despliegue automático.
