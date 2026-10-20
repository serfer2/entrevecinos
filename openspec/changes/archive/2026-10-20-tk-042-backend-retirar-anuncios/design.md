## Context

El listado ya excluye `hidden` (TK-028) y `ListingVisibility` (TK-036) responde 404 a quien no es autor ni gestor.

## Decisions

- **`ChangeListingStatus`** (aplicación): solo gestores (`COMMUNITY_MANAGERS` o `platform_admin`); `active | reserved | completed → hidden` y `hidden → active`. El mismo estado → 409 «El anuncio ya está en ese estado.»; otra transición → 409 «Transición de estado no permitida.». Diseñado para que TK-044 añada las transiciones del autor.
- **Petición** limitada a `hidden` y `active` (otros valores → 422 hasta TK-044).
- **Auditoría mínima:** `hidden_by` (FK a `users`, `SET NULL`) y `hidden_at`, que se vacían al restaurar. Restaurar deja el anuncio `active` aunque estuviera reservado.

## Risks / Trade-offs

- [Sin motivo de la retirada] → lo cubrirá el sistema de denuncias (post-MVP).
