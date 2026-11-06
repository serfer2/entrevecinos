# ci-checks Specification

## Purpose
Integración continua en GitHub Actions: comprobaciones de la API, la web, la infraestructura y las imágenes en cada pull request, regla de documentación de la infraestructura, Dependabot y protección de `main`.
## Requirements
### Requirement: Comprobaciones en cada pull request
El *workflow* `CI` (`.github/workflows/ci.yml`) SHALL ejecutarse en cada *pull request* y como `workflow_call` (en `main`, desde el despliegue de `deploy.yml`), con los trabajos `api` (`ruff check`, `ruff format --check` y `pytest` con PostgreSQL), `web` (`lint`, `typecheck` y `test`), `infra` (`make tf-lint` y `shellcheck`), `images` (etapas `prod` de `api` y `web` para `linux/arm64`, sin publicar) y `docs-infra`. Los trabajos MUST usar los objetivos `make ci-api`, `make ci-web`, `make tf-lint` y `make shellcheck`, que también se ejecutan en local. Solo en *pull requests* una ejecución nueva cancela la anterior.

#### Scenario: Pull request correcto
- **WHEN** abro un *pull request* a `main` que pasa todas las comprobaciones
- **THEN** los cinco trabajos aparecen en verde en el *pull request*

#### Scenario: Prueba rota
- **WHEN** un *pull request* rompe una prueba o el formato
- **THEN** el trabajo correspondiente falla y GitHub no permite fusionarlo

#### Scenario: Comprobaciones en main
- **WHEN** se fusiona un *pull request* en `main`
- **THEN** las comprobaciones se ejecutan una sola vez, dentro del despliegue

### Requirement: Documentación de la infraestructura
El trabajo `docs-infra` SHALL fallar en un *pull request* que cambia `infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml` o `.github/workflows/**` sin cambiar `infra/aws/README.md`, con el mensaje «Este pull request cambia la infraestructura: actualiza infra/aws/README.md o añade la etiqueta sin-cambios-en-doc-infra si el cambio no afecta a la documentación.», salvo que el *pull request* tenga la etiqueta `sin-cambios-en-doc-infra`.

#### Scenario: Infraestructura sin guía
- **WHEN** un *pull request* cambia `infra/aws/modules/edge/main.tf` sin tocar `infra/aws/README.md`
- **THEN** `docs-infra` falla con el mensaje

#### Scenario: Con la etiqueta
- **WHEN** añado la etiqueta `sin-cambios-en-doc-infra` a ese *pull request*
- **THEN** `docs-infra` se vuelve a ejecutar y pasa

#### Scenario: Sin infraestructura
- **WHEN** un *pull request* solo cambia `apps/web/`
- **THEN** `docs-infra` pasa

### Requirement: Workflow seguro
El *workflow* SHALL tener `permissions: contents: read`, fijar las acciones externas por SHA, cancelar ejecuciones antiguas de la misma rama y MUST NOT usar secretos ni credenciales de AWS.

#### Scenario: Revisión del fichero
- **WHEN** reviso `.github/workflows/ci.yml`
- **THEN** solo hay permisos de lectura, cada `uses:` lleva un SHA y no aparece ningún `secrets.`

### Requirement: Dependencias y protección de main
`.github/dependabot.yml` SHALL proponer cada semana actualizaciones de `github-actions`, `uv`, `npm`, `docker`, `docker-compose` y `terraform`. La rama `main` MUST exigir los cinco trabajos como comprobaciones obligatorias antes de fusionar.

#### Scenario: Fusión bloqueada
- **WHEN** un *pull request* tiene una comprobación obligatoria en rojo
- **THEN** el botón de fusión está desactivado

