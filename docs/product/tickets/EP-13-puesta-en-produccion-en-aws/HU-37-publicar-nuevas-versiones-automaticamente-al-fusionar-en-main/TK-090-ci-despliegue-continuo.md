# TK-090 · CI: despliegue continuo en producción

| Campo | Valor |
|---|---|
| **Tipo** | CI / despliegue |
| **Componente** | `.github/workflows/deploy.yml` (nuevo), entorno `production` en GitHub |
| **Historia** | HU-37 Publicar nuevas versiones automáticamente al fusionar en `main` (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-087, TK-088, TK-089 |
| **Referencias** | TK-086 (`deploy.sh` y documento `entrevecinos-deploy`), TK-088 (rol OIDC); `aws-actions/configure-aws-credentials`, `aws-actions/amazon-ecr-login` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Tras TK-086 y TK-087 se puede desplegar a mano: construir las imágenes, subirlas a ECR y lanzar el documento de SSM. TK-089 comprueba cada cambio y TK-088 permite a GitHub obtener credenciales temporales. Falta unirlo para que cada fusión en `main` llegue a producción sin pasos manuales.

**Objetivo:** un *workflow* que, al fusionar en `main` y pasar las comprobaciones, publique las imágenes del *commit*, despliegue en la instancia y compruebe la URL pública.

## 2. Alcance

**Incluye**
- `.github/workflows/deploy.yml` (`on: push` a `main` y `workflow_dispatch` para volver a desplegar un SHA concreto):
  1. **checks**: reutiliza `ci.yml` (`workflow_call`);
  2. **publish** (`needs: checks`, entorno `production`, `permissions: id-token: write, contents: read`): asume `entrevecinos-github-deploy` por OIDC, construye `api` y `web` (`prod`, `linux/arm64`), las sube a ECR con la etiqueta del SHA del *commit* y obtiene sus *digests*;
  3. **deploy** (`needs: publish`): `aws ssm send-command` con `entrevecinos-deploy` y los *digests*; espera al resultado (`aws ssm wait command-executed`) y muestra la salida del script;
  4. **smoke**: `curl` a `https://entrevecinos.org/` y a `/login` esperando `200` (o la redirección prevista), con reintentos durante 2 minutos.
- `concurrency: production` sin cancelación: nunca dos despliegues a la vez.
- Entorno `production` en GitHub: variables `AWS_ROLE_ARN`, `AWS_REGION`, `ECR_REGISTRY`, `INSTANCE_ID`, `PUBLIC_URL=https://entrevecinos.org`; aprobación manual opcional (*required reviewers*).
- Resumen del despliegue en `$GITHUB_STEP_SUMMARY` (SHA, *digests*, resultado).

**No incluye**
- Cambios de infraestructura con Terraform desde CI (se aplican a mano, TK-088 §8).
- Despliegues de *preview* por *pull request*.

## 3. Requisitos técnicos

- La etiqueta del SHA es inmutable en ECR (TK-080): volver a ejecutar el mismo SHA reutiliza la imagen existente en lugar de fallar al subirla.
- El *workflow* no recibe ni imprime secretos de la aplicación; `deploy.sh` los lee en la instancia.
- Si `deploy.sh` hace la vuelta atrás (TK-086 AC4), el comando de SSM termina con error y el *workflow* falla.
- El *smoke test* comprueba también una cabecera de seguridad (`Strict-Transport-Security`) para detectar despliegues sin la configuración de producción.

## 4. Criterios de aceptación

**AC1 — Despliegue continuo (HU-37 AC2)**
- **Given** un *commit* fusionado en `main` que pasa las comprobaciones
- **When** termina `deploy.yml`
- **Then** la instancia ejecuta las imágenes de ese SHA, las migraciones se han aplicado y el *smoke test* ha pasado

**AC2 — Credenciales temporales (HU-37 AC3)**
- **Given** la ejecución del *workflow*
- **When** reviso sus registros
- **Then** las credenciales proceden de `AssumeRoleWithWebIdentity` y no se ha usado ningún secreto de AWS

**AC3 — Vuelta atrás visible (HU-37 AC4)**
- **Given** un *commit* cuya API no arranca
- **When** se despliega
- **Then** el *workflow* falla en el paso `deploy` y producción sigue sirviendo la versión anterior

**AC4 — Un despliegue a la vez**
- **Given** dos fusiones seguidas en `main`
- **When** se ejecutan sus *workflows*
- **Then** el segundo despliegue espera a que termine el primero

## 5. Plan de tareas

1. *Workflow* con `checks` reutilizado y `publish`.
2. Paso `deploy` por SSM con espera y salida.
3. *Smoke test* y resumen.
4. Entorno `production` y variables en GitHub.
5. Prueba con un cambio real y con un fallo provocado.

## 6. Verificación

Desde la interfaz web de GitHub (no hace falta instalar `gh` en el equipo):

- **Ejecuciones del despliegue (AC1, AC4):** `https://github.com/serfer2/entrevecinos/actions/workflows/deploy.yml` → lista de ejecuciones por *commit*; dos fusiones seguidas muestran la segunda «Waiting» hasta que termina la primera (`concurrency`).
- **Registro y resumen (AC1, AC3):** abrir una ejecución → trabajos `checks`, `publish`, `deploy` y `smoke`; el resumen muestra el SHA y los *digests*, y el registro de `deploy` incluye la salida de `deploy.sh` (o el error y la vuelta atrás).
- **Credenciales temporales (AC2):** registro del paso `configure-aws-credentials` → «Assuming role with OIDC»; en *Settings* → *Secrets and variables* → *Actions* no hay claves de AWS, solo variables del entorno `production`.
- **Entorno `production`:** *Settings* → *Environments* → `production`, con sus variables y, si se activa, la aprobación manual.

Desde la terminal, con las herramientas ya disponibles:

```bash
aws ssm list-command-invocations --details --max-items 1 --profile entrevecinos
curl -sI https://entrevecinos.org/ | head -1
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Al menos un despliegue real y una vuelta atrás probados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Aprobación manual:** con el entorno `production` se puede exigir aprobación antes de `publish`. Más seguro, pero ya no es «automático»; se recomienda dejarla desactivada en el MVP y activarla si hay más personas con permiso de escritura.
- **SSM frente a SSH:** SSM evita abrir el puerto 22 y guardar claves SSH en GitHub; a cambio, el registro de la ejecución es menos inmediato.
- **Construcción duplicada:** `ci.yml` construye las imágenes sin publicar y `publish` las vuelve a construir; la caché de `buildx` lo reduce. Alternativa: publicar ya en `ci.yml` cuando sea `main`.
