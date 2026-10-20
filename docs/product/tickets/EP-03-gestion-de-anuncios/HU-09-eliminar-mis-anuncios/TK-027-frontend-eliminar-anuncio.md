# TK-027 · Frontend: eliminar un anuncio propio con confirmación

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/`, detalle del anuncio) |
| **Historia** | HU-09 Eliminar mis anuncios (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-018 (`ConfirmDialog`), TK-026, TK-037 (detalle del anuncio) |
| **Referencias** | `user-stories.md` HU-09; `docs/api/paths/listings_listing_id.yaml` (`delete`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-09 pide confirmar antes de eliminar, que el anuncio desaparezca del listado y de las búsquedas, y que no se ofrezca la opción a quien no es el autor.

**Objetivo:** añadir el botón «Eliminar anuncio» con confirmación en el detalle del anuncio, solo para su autor.

## 2. Alcance

**Incluye**
- Botón «Eliminar anuncio» en el detalle (TK-037), solo si soy el autor.
- Confirmación con `ConfirmDialog` (TK-018).
- *Server Action* `deleteListing(listingId)`.

**No incluye**
- Retirada por administradores (TK-043). Aunque la API permite que un administrador también borre, en la interfaz el administrador usa «Retirar anuncio» (reversible) (asumido).

## 3. Requisitos técnicos

### 3.1 Botón y confirmación

- Botón secundario de estilo destructivo «Eliminar anuncio», junto a «Editar anuncio».
- Diálogo: título «¿Eliminar este anuncio?», texto «Dejará de verse en la comunidad. Esta acción no se puede deshacer.», botones «Eliminar» y «Cancelar» (foco inicial en «Cancelar»).

### 3.2 *Server Action* `deleteListing`

- `requireUser()`; valida el UUID; `DELETE /v1/listings/{id}`.
- `204` → `revalidatePath` del listado de la comunidad y `redirect("/comunidades/<communityId>?eliminado=1")`, que muestra «Anuncio eliminado.».
- `404` → el anuncio ya no existe: redirige igualmente con «Este anuncio ya no estaba disponible.».
- `403` → «No puedes eliminar este anuncio.». Red o `5xx` → error general, sin salir del detalle.
- El `communityId` para redirigir se obtiene del anuncio en el servidor, no del formulario.

### 3.3 Pruebas

- `deleteListing`: `204`, `404`, `403`, red.
- Detalle: el botón solo aparece al autor; cancelar no llama a la acción.

## 4. Criterios de aceptación

**AC1 — Confirmación (HU-09 AC1)**
- **Given** que soy el autor y estoy en el detalle de mi anuncio
- **When** pulso «Eliminar anuncio»
- **Then** se me pide confirmar; si cancelo, no pasa nada

**AC2 — Eliminación correcta (HU-09 AC2)**
- **Given** que he confirmado
- **When** vuelvo al listado de la comunidad
- **Then** veo «Anuncio eliminado.» y el anuncio ya no aparece ni en el listado ni en las búsquedas; su URL muestra «Anuncio no disponible»

**AC3 — Solo el autor (HU-09 AC3)**
- **Given** un anuncio de otro vecino
- **When** abro su detalle
- **Then** no veo la opción de eliminarlo

## 5. Plan de tareas

1. *Server Action* `deleteListing` con pruebas.
2. Botón y diálogo en el detalle, condicionados al autor.
3. Mensaje en el listado y verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Autor: detalle → «Eliminar anuncio» → «Cancelar» (sigue) → «Eliminar anuncio» → «Eliminar» → listado sin el anuncio
# Buscar su título (TK-031) → sin resultados; abrir su URL → «Anuncio no disponible»
# Otro miembro: sin botón
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] El diálogo es accesible con teclado.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Deshacer:** no disponible; el texto del diálogo lo deja claro.
