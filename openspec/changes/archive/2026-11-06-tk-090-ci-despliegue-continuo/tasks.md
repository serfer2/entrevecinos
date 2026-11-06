## 1. Workflow

- [x] 1.1 `deploy.yml`: `checks` (reutiliza `ci.yml`) y `publish` (rol, ECR, imágenes `arm64`, reutilización de etiquetas, *digests*)
- [x] 1.2 `deploy`: `entrevecinos-deploy` por SSM, espera, salida y fallo si no es `Success`
- [x] 1.3 `smoke` y resumen; `concurrency` `production`; `workflow_dispatch` limitado a commits de `main`
- [x] 1.4 `ci.yml` sin `push` a `main` y sin cancelar cuando lo llama el despliegue; `actionlint` sin avisos

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «Despliegue continuo», «Integración continua», «Despliegue manual» y «Decisiones»

## 3. Verificación

- [x] 3.1 Fusión de PR #6 en `main`: primer despliegue automático correcto (AC1, AC2)
- [x] 3.2 Vuelta atrás con un commit cuya API no arranca (AC3) y su reversión
- [x] 3.3 Dos fusiones seguidas: la segunda espera (AC4)
