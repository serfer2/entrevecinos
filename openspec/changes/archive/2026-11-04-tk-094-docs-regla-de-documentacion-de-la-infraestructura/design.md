## Context

La Épica 13 crea toda la infraestructura de producción y concentra su documentación en `infra/aws/README.md` (guía, *runbook*, costes, decisiones y evolución). Aún no existe `infra/aws/` ni `.github/workflows/`. TK-094 pedía también una comprobación `docs-infra` en CI; el proyecto decidió implementar ahora solo las reglas y aplazar la comprobación a TK-089, que crea el primer *workflow*.

## Goals / Non-Goals

**Goals:**
- Que OpenSpec, los agentes y las personas sepan desde ya que todo cambio de infraestructura actualiza `infra/aws/README.md`.
- Que `infra/aws/README.md` exista con la estructura que irán rellenando los tickets.

**Non-Goals:**
- Comprobación automática en CI (pasa a TK-089).
- Contenido de la guía (TK-078 a TK-093) y de las decisiones (TK-095).

## Decisions

- **Lista única de rutas** (`infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml`, `.github/workflows/**`), repetida literalmente en las tres reglas para que no diverjan. Alternativa descartada: un fichero de configuración compartido (p. ej. `CODEOWNERS`); añade una pieza más sin beneficio mientras no haya CI.
- **Esqueleto de `infra/aws/README.md` ahora**, con una sección por tema y el ticket que la completa. Así la regla tiene destino y cada ticket sabe qué sección tocar. TK-078 lo ampliará en lugar de crearlo.
- **`infra/docker-compose.yml` (desarrollo) fuera de las rutas**: sus cambios no afectan a producción y ya los documenta `infra/README.md`.
- **Reglas en `openspec/config.yaml` en las mismas claves y estilo** que las existentes (una frase por regla, en español); el `context` gana un párrafo de infraestructura de producción en vez de reescribir el de desarrollo.
- **Aplazamiento de `docs-infra`**: TK-089 incorpora el trabajo en su alcance y TK-094 deja constancia de ello; el índice de tickets lo recoge.

## Risks / Trade-offs

- [Sin comprobación automática hasta TK-089, la regla depende de la disciplina] → reglas de OpenSpec y `AGENTS.md`, casilla en la plantilla de *pull request* y revisión.
- [El esqueleto puede quedarse con secciones vacías si se olvida un ticket] → cada sección cita su ticket; TK-093 revisa que no quede ninguna pendiente.
