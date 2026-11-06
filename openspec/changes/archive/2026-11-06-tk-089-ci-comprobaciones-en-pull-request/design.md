## Context

El repositorio es público. Las comprobaciones de `AGENTS.md` usan Compose (`api` con PostgreSQL, MinIO y Mailpit) y la imagen de la web. `make tf-lint` ya valida Terraform en contenedores sin credenciales. La instancia de producción es `arm64`.

## Goals / Non-Goals

**Goals:** mismas comprobaciones en local y en CI, fusión bloqueada si fallan, regla de documentación automática y *workflow* reutilizable por TK-090.

**Non-Goals:** publicar ni desplegar (TK-090); `terraform plan` contra AWS (sin identidad de lectura, TK-088).

## Decisions

- **Objetivos de `make` compartidos.** `ci-api` construye la imagen `dev` y ejecuta `ruff check`, `ruff format --check` y `pytest` con Compose (las pruebas `db` usan su PostgreSQL), como `AGENTS.md`. `ci-web` construye la etapa `dev` y ejecuta `lint`, `typecheck` y `test` con `docker run`, **sin montar el código**: en los *runners* el usuario no es el `node` (1000) de la imagen y el montaje de Compose fallaría al escribir. `shellcheck` analiza `infra/prod/**/*.sh`. El `.env` de CI es `.env.example`.
- **`images` en `ubuntu-24.04-arm`** (gratuitos en repositorios públicos): compilación nativa, sin QEMU. Matriz `api`/`web`, `build-push-action` con `push: false`, caché `type=gha` por servicio e imágenes base de ECR Public (`build-contexts`), como el despliegue manual, para no depender del límite de Docker Hub.
- **`docs-infra`** con `git diff --name-only origin/<base>...HEAD` (`fetch-depth: 0`): falla si cambia `infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml` o `.github/workflows/**` sin `infra/aws/README.md`, salvo con la etiqueta `sin-cambios-en-doc-infra`. Escucha `labeled`/`unlabeled` para reevaluarse al poner la etiqueta. En `push` a `main` se omite (un trabajo omitido cuenta como correcto para la protección).
- **Seguridad:** `permissions: contents: read` global; `persist-credentials: false`; acciones por SHA con su versión en comentario; el único *token* es el automático de solo lectura, que se pasa a tflint para descargar su *plugin*. Variables del *pull request* (`base_ref`, etiquetas) por `env`, nunca interpoladas en el *script*.
- **Dependabot** semanal para todos los ecosistemas del repositorio, incluidos `uv` (la API) y `docker-compose`.
- **Protección de `main` manual** (sin `gh` ni token de administración): *ruleset* con los cinco trabajos requeridos y una revisión.

## Risks / Trade-offs

- [Duración: la imagen `dev` de la API y Compose en frío] → objetivo < 15 min; la caché de `gha` acelera `images`.
- [Docker Hub en `api` (PostgreSQL, MinIO, Mailpit)] → los *runners* de GitHub tienen su propia cuota; si falla, réplicas de ECR Public.
- [Con un único mantenedor, «una revisión» bloquea sus propios *pull requests*] → el *ruleset* permite la omisión al administrador (*bypass*) o se exigen 0 revisiones; se documenta.
