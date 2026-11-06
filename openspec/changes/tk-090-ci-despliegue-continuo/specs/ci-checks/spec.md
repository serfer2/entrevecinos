## MODIFIED Requirements

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
