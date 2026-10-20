# TK-036 · Backend: detalle de un anuncio (`GET /v1/listings/{id}`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-14 Consultar el detalle de un anuncio (Épica 5) |
| **Prioridad** | Alta |
| **Depende de** | TK-022, TK-026 |
| **Referencias** | `docs/api/paths/listings_listing_id.yaml` (`get`); esquemas `Listing`, `ListingOwner`, `ListingImage` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-14 pide ver la información completa de un anuncio y de su anunciante, y un mensaje claro cuando el anuncio se ha eliminado o retirado. El contrato exige membresía aprobada en la comunidad del anuncio y oculta los anuncios `hidden` salvo a su autor y a los moderadores.

**Objetivo:** implementar `GET /v1/listings/{id}` con las reglas de visibilidad, que reutilizarán la lectura de imágenes (TK-021) y la edición (TK-024).

## 2. Alcance

**Incluye**
- Caso de uso `GetListing` y regla de visibilidad `ListingVisibility`.
- `Listing` con `owner`, `images` y `category_id`; el frontend obtiene el nombre de la categoría de `GET /v1/categories`.

**No incluye**
- Correo del anunciante (TK-038).
- Contador de visitas, anuncios relacionados (post-MVP).

## 3. Requisitos técnicos

### 3.1 Visibilidad

| Situación del anuncio | Quién lo ve | Respuesta para el resto |
|---|---|---|
| no existe o eliminado | nadie | **404** |
| `active`, `reserved` | miembros aprobados de su comunidad | **403** (no miembro o no aprobado) |
| `completed` | miembros aprobados (asumido: deja de listarse pero el enlace sigue funcionando) | **403** |
| `hidden` (retirado) | su autor y los `community_admin`/`moderator` de la comunidad, o `platform_admin` | **404** para el resto de miembros (HU-14 AC3 y HU-17 AC2: «no disponible»; no revela que existe) |

- TK-040 añade una regla: el anuncio de un autor sin membresía `approved` en la comunidad (bloqueado o expulsado) se trata como `hidden`.
- `ListingVisibility.can_view(user, listing, membership)` en la capa de aplicación, usada aquí, en la lectura de imágenes (TK-021 §3.3) y en el detalle del frontend.
- El orden de comprobación evita filtrar información: primero existencia y borrado (404), después membresía (403), después `hidden` (404).

### 3.2 Respuesta

- **200** `Listing` completo: `owner` (`id`, `full_name`, `phone`, `avatar_url`), `images` ordenadas, `status`, `published_at`, `updated_at`.
- Un anuncio cuyo autor ha sido eliminado (`users.deleted_at`) → **404** (asumido: el contrato oculta los anuncios de cuentas eliminadas, `users_me.yaml` `delete`).

### 3.3 Pruebas

- Matriz de §3.1 completa (autor, miembro, admin, moderador, pendiente, ajeno, `platform_admin`).
- Anuncio de una cuenta eliminada → **404**.
- Id mal formado → **422**; sin token → **401**.

## 4. Criterios de aceptación

**AC1 — Información del anuncio (HU-14 AC1)**
- **Given** que soy miembro aprobado y existe un anuncio activo en mi comunidad
- **When** llamo a `GET /v1/listings/{id}`
- **Then** recibo título, descripción, `category_id`, tipo, precio, imágenes ordenadas y `published_at`

**AC2 — Información del anunciante (HU-14 AC2)**
- **Given** el mismo anuncio
- **When** consulto `owner`
- **Then** contiene su nombre y su teléfono (o `null`)

**AC3 — Anuncio no disponible (HU-14 AC3)**
- **Given** un anuncio eliminado, o retirado por un administrador
- **When** lo pide un miembro que no es su autor ni administrador
- **Then** recibe `404`

**AC4 — Acceso restringido**
- **Given** un anuncio de una comunidad a la que no pertenezco
- **When** lo pido
- **Then** recibo `403`

## 5. Plan de tareas

1. `ListingVisibility` con pruebas unitarias (matriz completa).
2. `GetListing` y endpoint.
3. Usar `ListingVisibility` en la regla de lectura de imágenes (TK-021).
4. Pruebas de integración; verificación según la sección 6.

## 6. Verificación

```bash
curl -s http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $MIEMBRO"                          # 200
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $AJENO"   # 403
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/v1/listings/<eliminado> -H "Authorization: Bearer $MIEMBRO"  # 404
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La misma regla de visibilidad gobierna el detalle y las imágenes.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`403` frente a `404` para ajenos:** el contrato usa `403`, lo que revela que el id existe; los ids son UUID aleatorios, así que el riesgo es bajo.
