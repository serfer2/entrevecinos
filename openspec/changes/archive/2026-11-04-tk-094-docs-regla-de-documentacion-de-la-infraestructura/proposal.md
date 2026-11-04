## Why

HU-39: `infra/aws/README.md` será la guía de operación de producción y el registro de decisiones de arquitectura, pero ninguna regla del proyecto obliga a actualizarla cuando cambia la infraestructura, así que se quedaría desfasada sin que nadie lo note. Se implementa ahora, antes de los tickets de infraestructura de la Épica 13, para que todos queden sujetos a la regla. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-39-entender-las-decisiones-de-la-arquitectura-de-produccion-y-mantener-su-documentacion-al-dia/TK-094-docs-regla-de-documentacion-de-la-infraestructura.md`.

## What Changes

- `openspec/config.yaml`: el `context` describe la infraestructura de producción y las rutas de infraestructura; reglas nuevas en `proposal`, `design` y `tasks` que exigen actualizar `infra/aws/README.md` cuando un change toca esas rutas.
- `AGENTS.md`: viñeta «Infraestructura» en §Convenciones con las rutas y la obligación de actualizar `infra/aws/README.md`.
- `.github/pull_request_template.md` (nuevo): casilla «Si cambia la infraestructura, he actualizado `infra/aws/README.md`».
- `infra/aws/README.md` (nuevo): esqueleto con las secciones que completarán los tickets de la épica, para que la regla tenga destino desde ya.
- Alcance reducido (decisión del proyecto): la comprobación automática `docs-infra` en CI se aplaza a TK-089, que se actualiza para incluirla; TK-094 y el índice de tickets lo reflejan.

## Capabilities

### New Capabilities
- `infrastructure-documentation`: obligación de mantener `infra/aws/README.md` al día con cada cambio de las rutas de infraestructura, exigida por OpenSpec, por las instrucciones de los agentes y por la plantilla de *pull request*.

### Modified Capabilities

## Impact

- Ficheros: `openspec/config.yaml`, `AGENTS.md`, `.github/pull_request_template.md`, `infra/aws/README.md`, `infra/README.md` (enlace), `docs/product/tickets/` (TK-089, TK-094 y el índice).
- Sin cambios de código, de contrato de la API ni migraciones.
