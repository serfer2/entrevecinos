## 1. Comprobaciones

- [x] 1.1 `make ci-api`, `make ci-web` y `make shellcheck`; ejecutados en local
- [x] 1.2 `.github/workflows/ci.yml`: `api`, `web`, `infra`, `images` y `docs-infra`; `actionlint` sin avisos
- [x] 1.3 `.github/dependabot.yml`

## 2. Documentación

- [x] 2.1 `AGENTS.md` e `infra/aws/README.md` («Integración continua», protección de `main`, etiqueta y «Decisiones»)

## 3. Verificación en GitHub

- [x] 3.1 Etiqueta `sin-cambios-en-doc-infra` y protección de `main` (manual)
- [x] 3.2 *Pull request* de la rama: los cinco trabajos en verde (AC1, AC3)
- [x] 3.3 *Pull requests* de prueba: prueba rota bloqueada (AC2) y `docs-infra` con y sin etiqueta (AC2b)
