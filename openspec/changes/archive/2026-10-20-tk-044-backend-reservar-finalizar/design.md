## Context

TK-042 dejó `ChangeListingStatus` con la moderación (`hidden ↔ active`); TK-024 `EditableListing`.

## Decisions

| Actual | Nuevo | Quién | Resultado |
|---|---|---|---|
| `active` | `reserved` | autor | 200 |
| `reserved` | `active` | autor | 200 |
| `active`, `reserved` | `completed` | autor | 200 |
| `active`, `reserved`, `completed` | `hidden` | gestión | 200 |
| `hidden` | `active` | gestión | 200 |
| igual al actual | — | — | 409 «El anuncio ya está en ese estado.» |
| `completed` | `active`, `reserved` | autor | 409 «Un anuncio finalizado no puede cambiar de estado.» |
| otra | — | — | 409 «Transición de estado no permitida.» |

- **`active` es ambiguo:** desde `hidden` es moderación; desde `reserved`, el autor quita la reserva.
- **Permisos:** el autor debe seguir siendo miembro aprobado (403); con el anuncio retirado, 403 `ListingLocked`. Reservar o finalizar el anuncio de otro, aunque sea moderador, → 403. Un moderador que es el autor tiene ambas reglas.
- **Efectos:** solo `status` y `updated_at`; `published_at` no cambia. `EditableListing` bloquea los `completed` (403 «Este anuncio está finalizado y no se puede editar.»); eliminarlo sigue permitido.

## Risks / Trade-offs

- [`completed` irreversible] → un error del autor solo se corrige eliminando y volviendo a publicar.
