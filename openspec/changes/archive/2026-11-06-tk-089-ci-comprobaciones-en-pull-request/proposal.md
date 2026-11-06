## Why

HU-37 AC1: las comprobaciones de `AGENTS.md` solo se ejecutan en local y el repositorio no tiene *workflows*. Antes del despliegue automático (TK-090), todo cambio debe pasar pruebas, lint, validación de Terraform y la construcción de las imágenes de producción, y la regla de documentación de la infraestructura (TK-094) debe comprobarse sola. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-37-publicar-nuevas-versiones-automaticamente-al-fusionar-en-main/TK-089-ci-comprobaciones-en-pull-request.md`.

## What Changes

- `.github/workflows/ci.yml` (nuevo): en cada *pull request*, en `main` y como `workflow_call`, cinco trabajos en paralelo: `api`, `web`, `infra`, `images` (etapas `prod` `linux/arm64` en *runners* arm64 nativos, con caché de GitHub Actions, sin publicar) y `docs-infra` (solo en *pull requests*). Solo lectura, acciones fijadas por SHA, `concurrency` con cancelación y sin secretos.
- `Makefile`: `make ci-api`, `make ci-web` y `make shellcheck`, las mismas órdenes en local y en CI; `tf-lint` pasa `GITHUB_TOKEN` a tflint si existe.
- `.github/dependabot.yml` (nuevo): `github-actions`, `uv`, `npm`, `docker`, `docker-compose` y `terraform`, semanal.
- Configuración manual de GitHub, documentada: etiqueta `sin-cambios-en-doc-infra` y protección de `main` con los cinco trabajos y una revisión.
- `AGENTS.md` e `infra/aws/README.md` («Integración continua», «Decisiones»).

## Capabilities

### New Capabilities
- `ci-checks`: *workflow* de comprobaciones, regla automática de documentación de la infraestructura, Dependabot y protección de `main`.

### Modified Capabilities
_(ninguna)_

## Impact

- Nuevos: `.github/workflows/ci.yml`, `.github/dependabot.yml`. Cambiados: `Makefile`, `AGENTS.md`, `infra/aws/README.md`.
- Sin cambios en la aplicación ni en AWS. Coste: 0 (minutos gratuitos en repositorios públicos, también en *runners* arm64).
