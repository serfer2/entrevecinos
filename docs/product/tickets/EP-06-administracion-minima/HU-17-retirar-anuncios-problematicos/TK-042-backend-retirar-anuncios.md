# TK-042 · Backend: retirar y restaurar anuncios (`PATCH /v1/listings/{id}/status`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad y moderación |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-17 Retirar anuncios problemáticos (Épica 6) |
| **Prioridad** | Media |
| **Depende de** | TK-017, TK-036 |
| **Referencias** | `docs/api/paths/listings_listing_id_status.yaml`; esquemas `ListingStatusUpdate`, `ListingStatus` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-17 pide que el administrador retire los anuncios inapropiados, que dejen de aparecer en el listado y en las búsquedas, que quien intente abrirlos vea que no están disponibles, y que un miembro sin rol no pueda hacerlo. El contrato lo resuelve con el estado `hidden`, que solo un `community_admin`/`moderator` o `platform_admin` puede poner o quitar.

**Objetivo:** implementar `PATCH /v1/listings/{id}/status` para retirar (`hidden`) y restaurar (`active`) anuncios por moderación.

## 2. Alcance

**Incluye**
- Transiciones de moderación: `active | reserved | completed → hidden` y `hidden → active`.
- Registro de quién retiró el anuncio y cuándo (columnas nuevas, ver §3.2).

**No incluye (asumido)**
- Transiciones del autor (`active ↔ reserved`, `active | reserved → completed`): HU-09b, TK-044, que amplía este endpoint. Hasta entonces el autor recibe `403`.
- Notificar al autor (post-MVP).

## 3. Requisitos técnicos

### 3.1 Reglas

- Permiso: `community_admin` o `moderator` aprobado de la comunidad del anuncio, o `platform_admin` (`CommunityAccess.require_role`).
- **Petición** `{"status": "hidden" | "active"}`; otros valores → **422** en este ticket (TK-044 admite `reserved` y `completed`).
- `hidden`: solo desde `active`, `reserved` o `completed`. `active`: solo desde `hidden` (restaurar). Otras combinaciones → **409** `{"detail": "El anuncio ya está en ese estado."}` o de transición no permitida.
- Anuncio eliminado → **404**.
- **200** `Listing` con el estado nuevo.

### 3.2 Auditoría mínima (migración `0006`)

- `listing.hidden_by UUID NULL` (FK → `users.id`, `ON DELETE SET NULL`) y `listing.hidden_at TIMESTAMPTZ NULL`. Se rellenan al retirar y se vacían al restaurar (asumido: suficiente para saber quién lo hizo; el historial completo es post-MVP).
- Restaurar devuelve el anuncio a `active` aunque antes estuviera `reserved` (asumido; guardar el estado previo complicaría el modelo).

### 3.3 Efecto

- El listado (TK-028) ya excluye `hidden`, la búsqueda también (mismo filtro), y el detalle (TK-036) devuelve `404` a quien no es autor ni moderador. Las pruebas de este ticket lo comprueban de extremo a extremo.

### 3.4 Pruebas

- Admin retira (**200**) → desaparece del listado y de `q=…`; un miembro recibe **404** en el detalle; el autor y el admin lo ven con `status: hidden`.
- Admin restaura (**200**) → vuelve al listado.
- Miembro sin rol y autor → **403**; ajeno → **403**; transiciones inválidas → **409**; `status: reserved` → **422** (cambia a las reglas del autor con TK-044).
- Moderador de otra comunidad → **403**.

## 4. Criterios de aceptación

**AC1 — Retirada (HU-17 AC1)**
- **Given** que soy administrador y hay un anuncio inapropiado en mi comunidad
- **When** envío `PATCH …/status` con `{"status": "hidden"}`
- **Then** recibo `200` y el anuncio deja de aparecer en el listado y en las búsquedas

**AC2 — No accesible (HU-17 AC2)**
- **Given** un anuncio retirado
- **When** un miembro que no es su autor ni administrador lo pide
- **Then** recibe `404`

**AC3 — Restricción (HU-17 AC3)**
- **Given** que soy miembro sin rol de administrador
- **When** intento retirar el anuncio de otro vecino
- **Then** recibo `403`

**AC4 — Restaurar**
- **Given** un anuncio retirado por error
- **When** el administrador envía `{"status": "active"}`
- **Then** vuelve a aparecer en el listado y se vacían `hidden_by` y `hidden_at`

## 5. Plan de tareas

1. Migración `0006` (`hidden_by`, `hidden_at`).
2. Caso de uso `ModerateListing` con transiciones y pruebas unitarias.
3. Endpoint y pruebas de integración de extremo a extremo; verificación según la sección 6.

## 6. Verificación

```bash
curl -s -X PATCH http://localhost:8000/v1/listings/<id>/status -H "Authorization: Bearer $ADMIN" \
  -H 'Content-Type: application/json' -d '{"status":"hidden"}'
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $MIEMBRO"  # 404
curl -s -o /dev/null -w '%{http_code}\n' -X PATCH http://localhost:8000/v1/listings/<id>/status \
  -H "Authorization: Bearer $MIEMBRO" -H 'Content-Type: application/json' -d '{"status":"hidden"}'               # 403
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `pytest`, `ruff check` y `alembic check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Transiciones del autor:** las añade TK-044 sobre este mismo endpoint; conviene diseñar el caso de uso pensando en esa ampliación.
- **Motivo de la retirada:** no se registra; el sistema de denuncias (post-MVP) lo cubrirá.
