# TK-089 · CI: comprobaciones en cada *pull request*

| Campo | Valor |
|---|---|
| **Tipo** | CI / calidad |
| **Componente** | `.github/workflows/ci.yml` (nuevo), `.github/dependabot.yml` (nuevo), configuración del repositorio en GitHub |
| **Historia** | HU-37 Publicar nuevas versiones automáticamente al fusionar en `main` (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-078, TK-094 |
| **Referencias** | `AGENTS.md` («Verificación antes de dar un cambio por terminado» y «Infraestructura»); `Makefile`; TK-076 (prueba de alcance del MVP); TK-094 (regla de documentación de la infraestructura, cuya comprobación automática se implementa aquí) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Las comprobaciones de `AGENTS.md` (pruebas, lint y formato de la API y de la web) se ejecutan hoy solo en local. El repositorio no tiene *workflows*. Antes de desplegar automáticamente hace falta que todo cambio pase las mismas comprobaciones, más la validación de Terraform y la construcción de las imágenes de producción.

**Objetivo:** un *workflow* que se ejecute en cada *pull request* y en `main`, que el despliegue (TK-090) reutilice y que bloquee la fusión si falla.

## 2. Alcance

**Incluye**
- `.github/workflows/ci.yml` (`on: pull_request` y `push` a `main`, y `workflow_call` para reutilizarlo), con trabajos en paralelo:
  - **api**: construir la imagen `dev` con Compose y ejecutar `ruff check`, `ruff format --check` y `pytest` (incluidas las pruebas `@pytest.mark.db` con el servicio `db` de Compose), igual que en `AGENTS.md`;
  - **web**: `npm ci`, `lint`, `typecheck` y `test` en la imagen de la web;
  - **infra**: `terraform fmt -check`, `terraform validate` (sin *backend*), `tflint` y `checkov` sobre `infra/aws/`, `shellcheck` de `infra/prod/*.sh`;
  - **images**: construir las etapas `prod` de `api` y `web` para `linux/arm64` con `docker buildx` y caché de GitHub Actions, sin publicar;
  - **docs-infra** (solo en *pull requests*; trasladado desde TK-094): si algún fichero cambiado está en las rutas de infraestructura (`infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml`, `.github/workflows/**`) y `infra/aws/README.md` no ha cambiado, falla con «Este *pull request* cambia la infraestructura: actualiza `infra/aws/README.md` o añade la etiqueta `sin-cambios-en-doc-infra` si el cambio no afecta a la documentación.»; la etiqueta `sin-cambios-en-doc-infra` (que se crea en el repositorio) lo omite. Usa `git diff --name-only origin/<base>...HEAD` con `fetch-depth: 0`, sin secretos.
- Seguridad del *workflow*: `permissions: contents: read` por defecto; acciones de terceros fijadas por SHA; `concurrency` por rama con cancelación de ejecuciones antiguas; sin secretos en los trabajos de *pull request*.
- `.github/dependabot.yml` para `github-actions`, `pip` (uv), `npm`, `docker` y `terraform`, semanal.
- Protección de la rama `main` en GitHub (manual, documentada): exigir los cinco trabajos (`api`, `web`, `infra`, `images` y `docs-infra`) y una revisión.

**No incluye**
- Publicar imágenes ni desplegar (TK-090).
- `terraform plan` contra AWS en *pull requests* (opcional, ver §8).

## 3. Requisitos técnicos

- El *workflow* usa los mismos comandos que `AGENTS.md` para que CI y local no diverjan; si conviene, se añaden objetivos al `Makefile` (`make ci-api`, `make ci-web`) que ejecuten ambos.
- `.env` de CI generado a partir de `.env.example` (valores ficticios) en el propio trabajo.
- La construcción `arm64` en *runners* `x86_64` usa QEMU; si es muy lenta, usar *runners* `ubuntu-24.04-arm` (asumido: disponibles para repositorios públicos).
- Tiempo objetivo del *workflow* completo: menos de 15 minutos (asumido).

## 4. Criterios de aceptación

**AC1 — Comprobaciones completas (HU-37 AC1)**
- **Given** un *pull request* a `main`
- **When** termina el *workflow*
- **Then** se han ejecutado los trabajos `api`, `web`, `infra`, `images` y `docs-infra` y su resultado aparece en el *pull request*

**AC2 — Fusión bloqueada (HU-37 AC1)**
- **Given** un *pull request* que rompe una prueba o el formato
- **When** intento fusionarlo
- **Then** GitHub no lo permite hasta que las comprobaciones pasen

**AC2b — Documentación de la infraestructura (HU-39 AC2)**
- **Given** un *pull request* que cambia un fichero de `infra/aws/` sin tocar `infra/aws/README.md`
- **When** termina el *workflow*
- **Then** `docs-infra` falla con el mensaje acordado y el *pull request* no se puede fusionar; con la etiqueta `sin-cambios-en-doc-infra`, o actualizando la guía, pasa; y un *pull request* que solo cambia `apps/web/` lo pasa sin más

**AC3 — *Workflow* seguro**
- **Given** el fichero del *workflow*
- **When** lo reviso
- **Then** los permisos son de solo lectura, las acciones externas están fijadas por SHA y los trabajos de *pull request* no tienen acceso a secretos ni a AWS

## 5. Plan de tareas

1. Trabajos `api` y `web` reutilizando Compose.
2. Trabajo `infra`.
3. Trabajo `images` con `buildx` y caché.
4. Dependabot y protección de `main`.
5. *Pull request* de prueba que falle a propósito y otro que pase.

## 6. Verificación

Desde la interfaz web de GitHub (no hace falta instalar `gh` ni ninguna otra herramienta en el equipo):

- **Workflow registrado:** `https://github.com/serfer2/entrevecinos/actions` → en la barra lateral aparece «CI» (`ci.yml`) y su última ejecución en `main` está en verde.
- **Comprobaciones de un *pull request* (AC1):** en el *pull request*, pestaña *Checks* (o el bloque de estado al pie de *Conversation*) → aparecen los trabajos `api`, `web`, `infra`, `images` y `docs-infra` con su resultado; cada uno enlaza a su registro.
- **Documentación de la infraestructura (AC2b):** *pull request* de prueba que toca `infra/aws/` sin la guía → `docs-infra` en rojo con el mensaje; tras añadir la etiqueta o la guía, en verde.
- **Fusión bloqueada (AC2):** en un *pull request* con una prueba rota, el botón *Merge pull request* está desactivado con el aviso «Required statuses must pass before merging».
- **Protección de `main`:** *Settings* → *Branches* (o *Rules* → *Rulesets*) → la regla de `main` exige los cinco trabajos como *status checks* y una revisión aprobada.
- **Permisos y SHA (AC3):** revisión de `.github/workflows/ci.yml` en el *pull request* (bloque `permissions` y `uses: …@<sha>`).

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] El *workflow* pasa en `main`.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **`terraform plan` en *pull requests*:** muestra el impacto de los cambios de infraestructura, pero exige un rol de lectura asumible desde *pull requests* (TK-088) y expone en los registros detalles de la infraestructura. Se deja opcional; activarlo solo si el repositorio no acepta *pull requests* de *forks*.
- **Pruebas con base de datos en CI:** se usa el servicio `db` de Compose para no duplicar la configuración; alternativa: `services: postgres` de GitHub Actions.
- **Minutos de GitHub Actions:** gratuitos e ilimitados en repositorios públicos; si el repositorio es privado, la construcción `arm64` con QEMU consume muchos minutos.
