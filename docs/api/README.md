# API de EntreVecinos — especificación OpenAPI

Especificación OpenAPI 3.1 de la API REST (FastAPI). Está dividida en varios ficheros para que sea mantenible; el fichero único para importar en Swagger UI, Postman, etc. se genera en `dist/`.

## Estructura

```
docs/api/
├── openapi.yaml          # Raíz: info, servers, tags, seguridad global y mapa ruta → fichero
├── redocly.yaml          # Reglas de lint
├── paths/                # Un fichero por ruta (todas las operaciones HTTP de esa ruta)
├── components/
│   ├── schemas/          # Un fichero por schema (entidades, *Create, *Update, enums)
│   ├── parameters/       # Parámetros reutilizables (path params, paginación)
│   ├── responses/        # Errores comunes (400, 401, 403, 404, 409, 422)
│   └── securitySchemes/  # bearerAuth (JWT)
└── dist/
    └── openapi.bundled.yaml   # Generado: no editar a mano
```

Nombres de fichero de `paths/`: los segmentos de la ruta separados por `_`, sin llaves (`/communities/{community_id}/listings` → `communities_community_id_listings.yaml`).

## Convenciones

- **Autenticación:** `bearerAuth` (JWT) aplicado globalmente; los endpoints públicos (`/health`, `/auth/*`) declaran `security: []`.
- **Roles:** cada operación indica en su descripción quién puede invocarla (usuario autenticado, miembro aprobado, `community_admin`/`moderator`, `platform_admin`).
- **`x-mvp`:** `true` para operaciones del MVP (README §1.2), `false` para fases posteriores (mensajería, notificaciones, perfil profesional, denuncias, administración de plataforma).
- **`operationId`:** único, en camelCase (`listCommunityListings`).
- **Paginación:** `page` / `page_size`; respuesta `{items, page, page_size, total}` (`PageMeta` + `items`).
- **Errores:** `{"detail": "..."}` (`Error`); 422 con el formato de validación de FastAPI (`ValidationError`).
- **Request bodies:** `additionalProperties: false`; las actualizaciones parciales (`PATCH`) exigen `minProperties: 1`.
- **Imágenes en dos pasos:** `POST /media` (multipart) devuelve un `id`; después se asocia a un anuncio (`PUT /listings/{listing_id}/images`), a un perfil profesional o al avatar (`PATCH /users/me`).
- **Estados de anuncio:** la API expone `active`, `reserved`, `completed`, `hidden`. `draft` y `deleted` del modelo de datos son internos (un anuncio borrado responde 404).

## Cómo añadir o cambiar un endpoint

1. Crear o editar el fichero en `paths/` y, si es una ruta nueva, registrarla en `openapi.yaml`.
2. Crear los schemas necesarios en `components/schemas/` y añadirlos a la sección `components.schemas` de `openapi.yaml`.
3. Ejecutar lint y regenerar el bundle.

## Comandos

Desde `docs/api/`:

```bash
# Validar (usa redocly.yaml)
npx @redocly/cli lint openapi.yaml

# Generar el fichero único
npx @redocly/cli bundle openapi.yaml -o dist/openapi.bundled.yaml

# Previsualizar la documentación en el navegador
npx @redocly/cli preview-docs openapi.yaml
```

## Cambios

Cambios compatibles del contrato durante el desarrollo del MVP:

| Ticket | Cambio |
|---|---|
| TK-013 | `CommunityCreate`/`CommunityUpdate.description`: `maxLength: 2000`. |
| TK-017 | `MembershipError` (`Error` + `status`); respuestas `MembershipForbidden` (403) en las operaciones que exigen membresía aprobada y `MembershipConflict` (409) en `requestMembership`. |
| TK-022 | `ListingCreate`/`ListingUpdate.description`: `maxLength: 5000`; con precio y sin moneda se usa `EUR`. |
| TK-030 | `q` del listado: vacío equivale a no enviarlo; menos de 2 caracteres → 422; se ignoran las palabras de un carácter. |
| TK-038 | `ListingOwner.email` (obligatorio): canal de contacto del MVP junto con `phone`. |
| TK-044 | `updateListingStatus`: transiciones del autor (`active` ↔ `reserved`, → `completed` final) y 409 para transiciones no permitidas. |
| TK-050 | `createCommunity` crea la comunidad con `is_active: false` (pendiente de aprobación). `adminListCommunities` y `adminUpdateCommunity` pasan al MVP (`x-mvp: true`) para listar las pendientes y aprobarlas; `adminUpdateCommunity` solo admite `is_active: true`. |
| TK-052 | `createCommunity`: las comunidades que crea un `platform_admin` se crean activas (`is_active: true`). |
| TK-053 | `createCommunity`: 409 si el usuario ya tiene una comunidad pendiente de aprobación. |

## Resumen de endpoints

| Grupo | Operaciones | MVP |
|---|---|---|
| Sistema | `GET /health` | Sí |
| Autenticación | `POST /auth/register`, `POST /auth/token` | Sí |
| Usuarios | `GET/PATCH/DELETE /users/me`, `GET /users/me/memberships`, `GET /users/me/listings` | Sí |
| Categorías | `GET/POST /categories`, `PATCH /categories/{category_id}` | Sí |
| Comunidades | `GET/POST /communities`, `GET/PATCH /communities/{community_id}` | Sí |
| Membresías | `GET/POST /communities/{community_id}/memberships`, `PATCH/DELETE .../memberships/{user_id}` | Sí |
| Anuncios | `GET/POST /communities/{community_id}/listings`, `GET/PATCH/DELETE /listings/{listing_id}`, `PATCH .../status`, `PUT .../images` | Sí |
| Media | `POST /media`, `GET/DELETE /media/{asset_id}` | Sí |
| Mensajería | `POST /listings/{listing_id}/conversations`, `GET /conversations`, `GET/PATCH /conversations/{conversation_id}`, `GET/POST .../messages`, `POST .../read`, `DELETE /messages/{message_id}` | No |
| Notificaciones | `GET /notifications`, `PATCH /notifications/{notification_id}`, `POST /notifications/read-all` | No |
| Perfil profesional | `GET /professionals`, `GET /professionals/{user_id}`, `GET/PUT/DELETE /users/me/professional-profile`, servicios e imágenes del perfil | No |
| Denuncias | `POST /listings/{listing_id}/reports`, `GET /communities/{community_id}/reports`, `GET/PATCH /reports/{report_id}` | No |
| Administración | `GET /admin/communities`, `PATCH /admin/communities/{community_id}` (aprobación de comunidades) | Sí |
| Administración | `GET /admin/users`, `PATCH /admin/users/{user_id}` | No |
