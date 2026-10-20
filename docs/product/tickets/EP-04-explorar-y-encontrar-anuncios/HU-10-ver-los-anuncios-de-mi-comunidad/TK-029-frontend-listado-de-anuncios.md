# TK-029 · Frontend: listado de anuncios de la comunidad

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/`, `app/(privado)/comunidades/[communityId]/page.tsx`) |
| **Historia** | HU-10 Ver los anuncios de mi comunidad (Épica 4) |
| **Prioridad** | Alta |
| **Depende de** | TK-016, TK-023, TK-028 |
| **Referencias** | `user-stories.md` HU-10; `docs/api/paths/communities_community_id_listings.yaml` (`get`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La página de una comunidad muestra hasta ahora su nombre y el aviso de acceso (TK-016). HU-10 pide ver sus anuncios con título, tipo, precio, fotografía y fecha, primero los más recientes, con un mensaje cuando no haya ninguno.

**Objetivo:** mostrar en `/comunidades/[communityId]` el listado paginado de anuncios para los miembros aprobados, preparado para añadir la barra de búsqueda, filtros y orden de los tickets siguientes.

## 2. Alcance

**Incluye**
- Componente `ListingCard` y cuadrícula responsive.
- Formateo de precio (`Intl.NumberFormat("es-ES", { style: "currency" })`), fecha relativa o corta («hace 2 días» / «12 oct.») y etiqueta del tipo (`labels.ts`, TK-023).
- Estado vacío con invitación a publicar.
- Paginación (`Pagination`, TK-016) por `?page=`.
- Lectura de los parámetros de la URL en un único objeto `ListingSearchParams` que TK-031, TK-033 y TK-035 ampliarán.

**No incluye**
- Búsqueda, filtros y orden (TK-031, TK-033, TK-035). Detalle del anuncio (TK-037).

## 3. Requisitos técnicos

### 3.1 Página

- Server Component: `requireUser()`, comunidad y membresía (TK-016). Si la membresía no está aprobada, se muestra el aviso de TK-016 y **no** se llama al listado (la API respondería `403` igualmente).
- Miembro aprobado: `GET /v1/communities/{id}/listings?page=<n>&page_size=24` (asumido: 24 encaja en cuadrículas de 2, 3 y 4 columnas).
- Mensajes de la URL de otros tickets (`?publicado=1`, `?eliminado=1`) con `role="status"`.

### 3.2 `ListingCard`

- Enlace a `/anuncios/<id>` que envuelve la tarjeta.
- Portada (`mediaSrc`, `loading="lazy"`, `alt` = título); sin imágenes, un marcador neutro con el icono del tipo.
- Título (dos líneas como máximo), etiqueta del tipo, precio (o nada si no tiene; «Gratis» si el tipo es «Regalo» sin precio, asumido) y fecha de publicación (`<time dateTime>`).
- Anuncio `reserved`: etiqueta «Reservado».

### 3.3 Estado vacío (HU-10 AC3)

- «Todavía no hay anuncios en esta comunidad.» y botón «Publica el primero» (`/comunidades/<id>/anuncios/nuevo`).

### 3.4 Pruebas

- `ListingCard`: con y sin precio, con y sin imagen, reservado, regalo.
- Formateadores de precio, fecha y tipo.
- `ListingSearchParams`: `page` válido, inválido o ausente.
- Página: estado vacío, aviso de pendiente sin llamada al listado.

## 4. Criterios de aceptación

**AC1 — Listado (HU-10 AC1)**
- **Given** que soy miembro aprobado de una comunidad con anuncios
- **When** abro su página
- **Then** veo tarjetas con título, tipo, precio (si lo tienen), fotografía y fecha de publicación

**AC2 — Orden por defecto (HU-10 AC2)**
- **Given** que no he elegido ninguna ordenación
- **When** veo el listado
- **Then** los más recientes aparecen primero

**AC3 — Comunidad sin anuncios (HU-10 AC3)**
- **Given** una comunidad sin anuncios
- **When** abro su página
- **Then** veo «Todavía no hay anuncios en esta comunidad.» y el botón «Publica el primero»

**AC4 — Acceso restringido (HU-10 AC4)**
- **Given** que no soy miembro aprobado
- **When** abro la página de la comunidad
- **Then** no veo ningún anuncio, solo el aviso de mi estado

## 5. Plan de tareas

1. Formateadores y `ListingSearchParams` con pruebas.
2. `ListingCard` y cuadrícula responsive, con pruebas.
3. Página de la comunidad con listado, estado vacío y paginación.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Miembro aprobado con 30 anuncios: /comunidades/<id> → 24 tarjetas, «Siguiente» → 6
# Comunidad sin anuncios → estado vacío; pendiente → aviso
# Ventana de 360 px → una o dos columnas, sin scroll horizontal
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Las imágenes se cargan de forma diferida y tienen texto alternativo.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Coste de las imágenes:** cada portada pasa por `/media/<id>` → API → URL prefirmada. Con 24 tarjetas son 24 redirecciones; aceptable en el MVP. Las miniaturas (post-MVP) reducirían el peso.
