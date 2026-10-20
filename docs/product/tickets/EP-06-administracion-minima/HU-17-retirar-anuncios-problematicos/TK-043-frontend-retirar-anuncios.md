# TK-043 · Frontend: retirar y restaurar anuncios desde el detalle

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`ListingActions`, detalle del anuncio) |
| **Historia** | HU-17 Retirar anuncios problemáticos (Épica 6) |
| **Prioridad** | Media |
| **Depende de** | TK-018 (`ConfirmDialog`), TK-037, TK-042 |
| **Referencias** | `user-stories.md` HU-17 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-17 pide que el administrador retire un anuncio inapropiado, que deje de mostrarse y que a los miembros sin rol no se les ofrezca la opción.

**Objetivo:** añadir «Retirar anuncio» (y «Restaurar anuncio» para los retirados) en el detalle del anuncio, solo para administradores y moderadores de la comunidad.

## 2. Alcance

**Incluye**
- Botones en `ListingActions` cuando `canModerate` es verdadero.
- Aviso en el detalle de un anuncio retirado, visible para su autor y para los administradores.
- *Server Action* `moderateListing(listingId, status)`.

**No incluye**
- Listado de anuncios retirados en la gestión de la comunidad (sería útil, pero sin historia; asumido).

## 3. Requisitos técnicos

### 3.1 Botones

- `canModerate` se calcula en el servidor a partir de mi membresía en la comunidad del anuncio (`community_admin`, `moderator`) o de mi rol `platform_admin`.
- Anuncio visible → «Retirar anuncio» con confirmación: «¿Retirar este anuncio? Dejará de mostrarse en la comunidad. Podrás restaurarlo más tarde.».
- Anuncio `hidden` → «Restaurar anuncio», sin confirmación.
- En mi propio anuncio, si soy administrador, se muestran «Editar», «Eliminar» y «Retirar» (asumido: los roles se suman).

### 3.2 Anuncio retirado

- Para el autor y los administradores que todavía pueden verlo: banner «Este anuncio está retirado y no se muestra en la comunidad.» (`role="status"`). Para el autor, sin botón de editar (TK-024 §3.1).
- Para el resto, el detalle ya muestra «Anuncio no disponible» (TK-037).

### 3.3 *Server Action* `moderateListing`

- `requireUser()`; `PATCH /v1/listings/{id}/status`; `revalidatePath` del detalle y del listado.
- Éxito al retirar → `redirect("/comunidades/<communityId>?retirado=1")` con «Anuncio retirado.». Al restaurar → se queda en el detalle con «Anuncio restaurado.».
- `403` → «No puedes moderar este anuncio.». `409` → mensaje de la API. Red o `5xx` → error general.

### 3.4 Pruebas

- `ListingActions`: combinaciones de `isOwner`, `canModerate` y `status`.
- `moderateListing`: retirar, restaurar, `403`, `409`.

## 4. Criterios de aceptación

**AC1 — Retirada (HU-17 AC1)**
- **Given** que soy administrador y veo un anuncio inapropiado de mi comunidad
- **When** pulso «Retirar anuncio» y confirmo
- **Then** vuelvo al listado con «Anuncio retirado.» y el anuncio ya no aparece ni en el listado ni en las búsquedas

**AC2 — No accesible (HU-17 AC2)**
- **Given** un anuncio retirado
- **When** un miembro abre su enlace
- **Then** ve «Este anuncio no está disponible…»

**AC3 — Restricción (HU-17 AC3)**
- **Given** que soy miembro sin rol de administrador
- **When** abro el anuncio de otro vecino
- **Then** no veo la opción «Retirar anuncio»

**AC4 — Restaurar**
- **Given** un anuncio que retiré por error
- **When** abro su detalle y pulso «Restaurar anuncio»
- **Then** vuelve a aparecer en el listado de la comunidad

## 5. Plan de tareas

1. `canModerate` en el detalle y botones en `ListingActions`.
2. *Server Action* `moderateListing` y confirmación.
3. Banner de anuncio retirado.
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Admin: detalle → «Retirar anuncio» → confirmar → listado sin el anuncio; buscar su título → sin resultados
# Miembro: URL del anuncio → no disponible; autor: banner de retirado y sin «Editar»
# Admin: detalle del retirado → «Restaurar anuncio» → vuelve al listado
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Encontrar los anuncios retirados para restaurarlos:** solo por su URL; un listado de retirados en la gestión lo facilitaría.
