## Context

| | Operaciones |
|---|---|
| Contrato | 59 |
| `x-mvp: true` | 33 |
| Implementadas (`presentation/v1/`) | 27 |

Las 7 entidades sin tabla (mensajería, notificaciones, perfil profesional, denuncias) solo tienen operaciones `x-mvp: false`. La tabla completa entidades ↔ rutas está en TK-074 §1.

## Decisions

- **Las 6 operaciones sin implementar pasan a futuras** en lugar de implementarse: ninguna historia del MVP las necesita.
- **Se conservan las operaciones futuras en el contrato:** documenta también lo que está por venir.
- **`x-mvp` = implementada en el MVP:** definición única, verificable por TK-076.

## Risks / Trade-offs

- [Cambio de significado de `x-mvp`] → se documenta en `info.description`, en `docs/api/README.md` y en «Cambios».
