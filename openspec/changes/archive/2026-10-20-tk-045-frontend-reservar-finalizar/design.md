## Context

TK-044 añadió las transiciones del autor a `PATCH /v1/listings/{id}/status`; TK-043 la moderación en `ListingActions`.

## Decisions

| Estado | Acciones del autor | Confirmación |
|---|---|---|
| `active` | «Marcar como reservado», «Marcar como finalizado» | solo al finalizar |
| `reserved` | «Quitar reserva», «Marcar como finalizado» | solo al finalizar |
| `completed`, `hidden` | ninguna | — |

- **`changeListingStatus(formData)`** vuelve al detalle con `?cambio=reservado|disponible|finalizado`; `403`/`409`/otros con `?error=estado-…`. Sin JavaScript, el formulario envía sin confirmación.
- **Solo el autor** ve estas acciones; un administrador que no es el autor solo ve las de moderación.
- **Aviso de finalizado** visible para cualquier miembro que llegue por el enlace.

## Risks / Trade-offs

- [Finalizar es irreversible] → la confirmación lo advierte de forma explícita.
