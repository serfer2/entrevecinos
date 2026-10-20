# TK-037 · Frontend: página de detalle de un anuncio

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/`, `app/(privado)/anuncios/[listingId]/`) |
| **Historia** | HU-14 Consultar el detalle de un anuncio (Épica 5) |
| **Prioridad** | Alta |
| **Depende de** | TK-023 (`mediaSrc`, etiquetas), TK-029, TK-036 |
| **Referencias** | `user-stories.md` HU-14; `docs/api/paths/listings_listing_id.yaml` (`get`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Las tarjetas del listado (TK-029) enlazan a `/anuncios/<id>`, que aún no existe. HU-14 pide ver toda la información del anuncio y de su anunciante, y un mensaje cuando no está disponible.

**Objetivo:** crear la página de detalle, que además será el punto de entrada para editar (TK-025), eliminar (TK-027), contactar (TK-039) y retirar (TK-043).

## 2. Alcance

**Incluye**
- Página `/anuncios/[listingId]`: galería, título, tipo, categoría, precio, fecha, descripción y sección del anunciante (nombre).
- Página «Anuncio no disponible» para `404` (`not-found.tsx` del segmento).
- `403` → aviso de acceso (no soy miembro de esa comunidad).
- Zona de acciones (`ListingActions`) donde los tickets siguientes añaden sus botones según el usuario.
- Enlace «Volver a <comunidad>».

**No incluye**
- Datos de contacto del anunciante (TK-039).

## 3. Requisitos técnicos

### 3.1 Datos

- Server Component: `requireUser()`, `GET /v1/listings/{id}`, `GET /v1/categories` (nombre de la categoría) y `GET /v1/communities/{community_id}` (nombre para el enlace de vuelta), en paralelo cuando sea posible.
- `404` → `notFound()`; `403` → componente `Forbidden` con «No tienes acceso a los anuncios de esta comunidad.».
- `generateMetadata` → título de la pestaña «<título> · EntreVecinos».

### 3.2 Contenido

- **Galería** (`ListingGallery`, cliente): imagen principal (la portada) y miniaturas que la cambian; navegación con teclado (flechas) y botones accesibles («Imagen 2 de 3»). Sin imágenes, marcador neutro.
- Título (`h1`), etiqueta del tipo, «Reservado» si aplica, precio (o «Gratis» si es un regalo sin precio, TK-029), categoría y «Publicado el <fecha larga>»; «Actualizado el …» si `updated_at` difiere de forma significativa (asumido: más de 1 minuto).
- Descripción con los saltos de línea respetados (`whitespace-pre-line`), sin interpretar HTML.
- **Anunciante**: nombre (y espacio reservado para el contacto de TK-039).
- `ListingActions` recibe `isOwner` y `canModerate` (rol del usuario en la comunidad); en este ticket no muestra botones.

### 3.3 «Anuncio no disponible» (HU-14 AC3)

- `app/(privado)/anuncios/[listingId]/not-found.tsx`: «Este anuncio no está disponible. Puede que se haya eliminado o retirado.» y enlace a «Mis comunidades» (`/inicio`).

### 3.4 Pruebas

- `ListingGallery`: cambio de imagen por clic y por teclado; sin imágenes.
- Página: `200` con todos los campos, `404` → no disponible, `403` → sin acceso.
- Descripción con `<script>` se muestra como texto.

## 4. Criterios de aceptación

**AC1 — Información del anuncio (HU-14 AC1)**
- **Given** que estoy en el listado de mi comunidad
- **When** abro un anuncio
- **Then** veo su título, fotografías, descripción, categoría, tipo, precio (si lo tiene) y fecha de publicación

**AC2 — Información del anunciante (HU-14 AC2)**
- **Given** el detalle de un anuncio
- **When** miro la sección del anunciante
- **Then** veo su nombre (los datos de contacto llegan con TK-039)

**AC3 — No disponible (HU-14 AC3)**
- **Given** un anuncio eliminado o retirado
- **When** abro su enlace
- **Then** veo «Este anuncio no está disponible…»

**AC4 — Responsive y accesible**
- **Given** el detalle en un móvil de 360 px o solo con teclado
- **When** navego por la galería y el contenido
- **Then** no hay scroll horizontal y puedo recorrer todas las imágenes

## 5. Plan de tareas

1. `ListingGallery` con pruebas.
2. Página de detalle, `not-found.tsx` y `Forbidden`.
3. `ListingActions` (vacío) y enlace de vuelta.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Listado → tarjeta → detalle completo; cambiar imágenes con teclado
# Eliminar el anuncio (API) y recargar → «no está disponible»
# Usuario de otra comunidad con la URL → sin acceso
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Compartir el enlace fuera de la comunidad:** quien no es miembro ve el aviso de acceso, no una vista previa. Una vista pública limitada sería un cambio de producto.
