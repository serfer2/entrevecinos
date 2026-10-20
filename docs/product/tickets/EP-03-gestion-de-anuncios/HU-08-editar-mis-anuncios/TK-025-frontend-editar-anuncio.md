# TK-025 · Frontend: editar un anuncio propio

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/`, `app/(privado)/anuncios/[listingId]/editar/`) |
| **Historia** | HU-08 Editar mis anuncios (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-023, TK-024, TK-037 (punto de entrada desde el detalle) |
| **Referencias** | `user-stories.md` HU-08; `docs/api/paths/listings_listing_id.yaml` (`patch`), `listings_listing_id_images.yaml` (`put`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-08 pide que el autor pueda modificar su anuncio, que no pueda dejar vacíos el título ni la descripción, y que a los demás no se les ofrezca la edición.

**Objetivo:** crear la página `/anuncios/[listingId]/editar` reutilizando `ListingForm` e `ImagePicker` (TK-023), y el enlace «Editar» en el detalle del anuncio, visible solo para el autor.

## 2. Alcance

**Incluye**
- Página de edición con el formulario precargado (datos e imágenes).
- *Server Action* `updateListing`, que envía `PATCH` con los campos cambiados y `PUT …/images` si cambiaron las imágenes.
- Enlace «Editar anuncio» en el detalle (TK-037), solo si `owner.id` coincide con el usuario de la sesión.

**No incluye**
- Cambios de estado (reservado, finalizado): HU-09b, TK-045. «Editar» se oculta en anuncios finalizados (TK-045 §3.1).

## 3. Requisitos técnicos

### 3.1 Página `/anuncios/[listingId]/editar`

- `requireUser()` y `GET /v1/listings/{id}` (TK-036). `404` → página «Anuncio no disponible» (TK-037). Si el usuario no es el autor → `Forbidden` («Solo quien publicó el anuncio puede editarlo.»), sin llegar a pintar el formulario. La API vuelve a comprobarlo al guardar.
- `ListingForm` recibe `initialValues` (incluido el precio formateado con coma decimal) e `initialImages` (`asset_id`, `url`, portada).

### 3.2 *Server Action* `updateListing`

1. `requireUser()`; valida con `listingSchema`.
2. Vuelve a leer el anuncio con `GET` (no se confía en valores enviados por el navegador), calcula qué campos han cambiado y envía `PATCH` solo con ellos; si no hay cambios en los datos, no lo llama.
3. Si la lista de imágenes (orden o portada) ha cambiado, envía `PUT …/images`.
4. Éxito → `redirect("/anuncios/<id>?actualizado=1")`, que muestra «Anuncio actualizado.».
5. `403` → `Forbidden`. `422` → errores por campo. `400` → error de imágenes. Si el `PATCH` va bien y el `PUT` falla, se muestra «Los datos se han guardado, pero no las fotografías. Inténtalo de nuevo.» (no hay transacción entre ambas llamadas).

### 3.3 Pruebas

- Cálculo de cambios (sin cambios, solo precio, borrar precio, solo imágenes).
- `updateListing`: éxito, `422`, `403`, fallo parcial del `PUT`.
- Página: autor ve el formulario precargado; no autor ve `Forbidden`.

## 4. Criterios de aceptación

**AC1 — Edición correcta (HU-08 AC1)**
- **Given** que soy el autor y estoy en el detalle de mi anuncio
- **When** pulso «Editar anuncio», cambio título, precio y una fotografía, y guardo
- **Then** vuelvo al detalle con «Anuncio actualizado.» y la información nueva

**AC2 — Validación (HU-08 AC2)**
- **Given** que estoy editando mi anuncio
- **When** dejo vacío el título o la descripción y guardo (incluso sin validación del navegador)
- **Then** veo el error en el campo y, al volver al detalle, se mantiene la versión anterior

**AC3 — Solo el autor (HU-08 AC3)**
- **Given** un anuncio de otro vecino
- **When** abro su detalle o escribo la URL `/anuncios/<id>/editar`
- **Then** no veo «Editar anuncio» y la URL muestra «Solo quien publicó el anuncio puede editarlo.»

## 5. Plan de tareas

1. `ListingForm` con valores iniciales e `ImagePicker` con imágenes iniciales.
2. Cálculo de cambios y *Server Action* `updateListing` con pruebas.
3. Página de edición y enlace en el detalle.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Autor: detalle → «Editar anuncio» → cambiar título, precio y orden de fotos → guardar → detalle actualizado
# Vaciar el título (novalidate) → error; el detalle conserva el título anterior
# Otro miembro: sin enlace; /anuncios/<id>/editar → «Solo quien publicó…»
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Dos llamadas no atómicas (`PATCH` + `PUT`):** se informa del fallo parcial. Un endpoint único de edición evitaría el caso, pero cambiaría el contrato.
