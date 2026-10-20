# TK-044 · Backend: reservar y finalizar anuncios (`PATCH /v1/listings/{id}/status`, autor)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-09b Marcar mi anuncio como reservado o finalizado (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-024 (reglas de acceso del autor), TK-042 (endpoint de estado) |
| **Referencias** | `user-stories.md` HU-09b; `docs/api/paths/listings_listing_id_status.yaml`; esquemas `ListingStatusUpdate`, `ListingStatus` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-09b pide que el autor pueda marcar su anuncio como reservado, quitar la reserva y darlo por finalizado. El contrato ya lo resuelve con `PATCH /v1/listings/{id}/status`, que TK-042 implementó solo para la moderación (`hidden ↔ active`); el autor recibe hoy `403` y `reserved`/`completed` responden `422`.

**Objetivo:** ampliar el endpoint de TK-042 con las transiciones del autor: `active ↔ reserved` y `active | reserved → completed`, con `completed` como estado final.

## 2. Alcance

**Incluye**
- Transiciones del autor en el caso de uso `ChangeListingStatus` (renombrado desde `ModerateListing` de TK-042, que pasa a cubrir ambos casos).
- Bloqueo de la edición (`PATCH /listings/{id}` y `PUT …/images`) de un anuncio `completed`.
- Pruebas de la matriz completa de transiciones (autor y moderación).

**No incluye**
- Interfaz (TK-045).
- Reactivar un anuncio finalizado (asumido: `completed` es final; si se necesita, es una transición más).
- Historial de cambios de estado o fecha de reserva/finalización (post-MVP).

## 3. Requisitos técnicos

### 3.1 Matriz de transiciones

| Estado actual | Nuevo estado | Quién | Resultado |
|---|---|---|---|
| `active` | `reserved` | autor | **200** |
| `reserved` | `active` | autor | **200** (quitar la reserva) |
| `active`, `reserved` | `completed` | autor | **200** |
| `active`, `reserved`, `completed` | `hidden` | moderación (TK-042) | **200** |
| `hidden` | `active` | moderación (TK-042) | **200** (restaurar) |
| igual al actual | — | cualquiera con permiso | **409** `{"detail": "El anuncio ya está en ese estado."}` |
| `completed` | `active`, `reserved` | autor | **409** `{"detail": "Un anuncio finalizado no puede cambiar de estado."}` |
| cualquier otra combinación | — | — | **409** `{"detail": "Transición de estado no permitida."}` |

- El valor `active` es ambiguo (quitar la reserva o restaurar): se decide por el estado actual. Desde `hidden` aplica la regla de moderación; desde `reserved`, la del autor.
- La matriz vive en el dominio (`ListingStatus.can_transition(from, to, actor)` o equivalente), con pruebas unitarias; el caso de uso solo resuelve quién es el actor.

### 3.2 Permisos

- **Autor:** debe seguir siendo miembro aprobado de la comunidad (mismas reglas que TK-024 §3.1). Bloqueado o expulsado → **403**.
- **Anuncio `hidden`:** el autor no puede cambiar su estado → **403** `{"detail": "Este anuncio ha sido retirado por la administración de la comunidad."}` (mismo mensaje que TK-024).
- **Moderadores:** solo `hidden ↔ active` (TK-042). Marcar como reservado o finalizado el anuncio de otro → **403** (asumido: es una decisión del autor). Si el moderador es el autor, se aplican las dos reglas.
- Resto de usuarios → **403**. Anuncio inexistente o eliminado → **404**.
- Se elimina la respuesta `422` de TK-042 para `reserved` y `completed`; los valores fuera del enum siguen respondiendo **422**.

### 3.3 Efectos

- Solo cambian `status` y `updated_at`; `published_at` no se toca (quitar la reserva no «sube» el anuncio, asumido).
- **Listado y búsqueda** (TK-028): ya incluyen `reserved` y excluyen `completed`; no cambian.
- **Detalle** (TK-036): un `completed` sigue visible para los miembros por su enlace; no cambia.
- **Edición:** `UpdateListing` y `ReplaceListingImages` (TK-024) responden **403** `{"detail": "Este anuncio está finalizado y no se puede editar."}` si el anuncio es `completed`. Eliminarlo (TK-026) sigue permitido (asumido).
- **200** `Listing` con el estado nuevo.

### 3.4 Pruebas

- Unitarias: matriz de §3.1 completa, incluido el actor (autor, moderador, moderador-autor).
- Integración:
  - El autor reserva → `200`, el anuncio sigue en el listado con `status: reserved`; quita la reserva → `active`.
  - El autor finaliza → `200`, desaparece del listado y de `q=…`, el detalle sigue respondiendo `200` a un miembro.
  - Finalizado → reservar o activar → **409**; editar o cambiar imágenes → **403**; eliminar → **204**.
  - Otro miembro → **403**; moderador sobre anuncio ajeno con `reserved` → **403**; autor bloqueado → **403**; anuncio `hidden` y autor → **403**.
  - Las pruebas de moderación de TK-042 siguen pasando sin cambios, salvo la que esperaba `422` para `reserved`.

## 4. Criterios de aceptación

**AC1 — Reservar (HU-09b AC1)**
- **Given** que soy el autor de un anuncio `active`
- **When** envío `PATCH …/status` con `{"status": "reserved"}`
- **Then** recibo `200` con `status: "reserved"` y el anuncio sigue apareciendo en el listado

**AC2 — Quitar la reserva (HU-09b AC2)**
- **Given** que soy el autor de un anuncio `reserved`
- **When** envío `{"status": "active"}`
- **Then** recibo `200` con `status: "active"`

**AC3 — Finalizar (HU-09b AC3)**
- **Given** que soy el autor de un anuncio `active` o `reserved`
- **When** envío `{"status": "completed"}`
- **Then** recibo `200`, deja de aparecer en el listado y en las búsquedas, y cualquier cambio de estado o edición posterior se rechaza (`409` / `403`)

**AC4 — Solo el autor (HU-09b AC4)**
- **Given** un anuncio de otro vecino
- **When** intento reservarlo o finalizarlo, aunque sea moderador de la comunidad
- **Then** recibo `403` y el anuncio no cambia

## 5. Plan de tareas

1. Matriz de transiciones en el dominio con pruebas unitarias.
2. Caso de uso `ChangeListingStatus` (autor y moderación) a partir de `ModerateListing`.
3. Bloqueo de la edición de anuncios `completed` en TK-024.
4. Pruebas de integración de §3.4; verificación según la sección 6.

## 6. Verificación

```bash
curl -s -X PATCH http://localhost:8000/v1/listings/<id>/status -H "Authorization: Bearer $AUTOR" \
  -H 'Content-Type: application/json' -d '{"status":"reserved"}'                                       # 200
curl -s -X PATCH http://localhost:8000/v1/listings/<id>/status -H "Authorization: Bearer $AUTOR" \
  -H 'Content-Type: application/json' -d '{"status":"completed"}'                                      # 200
curl -s -o /dev/null -w '%{http_code}\n' -X PATCH http://localhost:8000/v1/listings/<id>/status \
  -H "Authorization: Bearer $AUTOR" -H 'Content-Type: application/json' -d '{"status":"active"}'       # 409
curl -s -o /dev/null -w '%{http_code}\n' -X PATCH http://localhost:8000/v1/listings/<otro>/status \
  -H "Authorization: Bearer $MIEMBRO" -H 'Content-Type: application/json' -d '{"status":"reserved"}'   # 403
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La matriz de transiciones está en el dominio y cubierta por pruebas unitarias.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`completed` irreversible:** un error del autor no se puede deshacer (solo eliminar y volver a publicar). Si negocio lo pide, se añade `completed → active`.
- **Moderador que retira y restaura un anuncio reservado:** vuelve a `active` (TK-042 §3.2); el autor puede volver a reservarlo.
