# TK-026 · Backend: eliminar un anuncio (`DELETE /v1/listings/{id}`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-09 Eliminar mis anuncios (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-022 |
| **Referencias** | `docs/api/paths/listings_listing_id.yaml` (`delete`); `readme.md` §3.2 (borrado lógico de `listing`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-09 pide que el autor retire un anuncio que ya no es válido, y que desaparezca del listado y de las búsquedas. El contrato define un borrado lógico (`deleted_at`) que puede hacer el autor, un `community_admin` o `moderator` de la comunidad, o un `platform_admin`.

**Objetivo:** implementar `DELETE /v1/listings/{id}` con borrado lógico y asegurar que un anuncio eliminado no aparece en ninguna lectura.

## 2. Alcance

**Incluye**
- Caso de uso `DeleteListing` con las reglas de permiso del contrato.
- Filtro común «no eliminado» en todas las consultas de anuncios.

**No incluye**
- Retirada por moderación (`hidden`, reversible): TK-042. El borrado es la opción del autor; la retirada, la del administrador (HU-09 AC3 remite a HU-17).
- Borrado de las imágenes en MinIO: se conservan (ver §8).

## 3. Requisitos técnicos

### 3.1 Reglas

- Puede borrar: el autor (aunque haya dejado de ser miembro, asumido: retirar lo propio siempre está permitido), un `community_admin` o `moderator` aprobado de la comunidad del anuncio, o un `platform_admin` (vía `CommunityAccess`, TK-017).
- Efecto: `deleted_at = now()` y `status = deleted`. No se borran filas.
- **204** sin cuerpo. **404** si no existe o ya estaba eliminado (borrar dos veces → `404`, asumido). **403** si no tiene permiso.

### 3.2 Filtro «no eliminado»

- El repositorio de anuncios aplica `deleted_at IS NULL` por defecto en todas las lecturas (`get`, listados, búsqueda, «mis anuncios», regla de lectura de imágenes de TK-021). Las pruebas lo comprueban en cada lectura existente.

### 3.3 Pruebas

- Autor borra (**204**) y después: `GET /v1/listings/{id}` → **404** (cuando exista, TK-036), no aparece en el listado de la comunidad (TK-028), sus imágenes dejan de ser legibles para los miembros (**403** en `GET /v1/media/{id}`), pero sí para su autor.
- Administrador de la comunidad borra el anuncio de otro (**204**).
- Miembro no autor (**403**), usuario de otra comunidad (**403**), id inexistente o ya borrado (**404**).

## 4. Criterios de aceptación

**AC1 — Eliminación correcta (HU-09 AC2)**
- **Given** que soy el autor de un anuncio
- **When** envío `DELETE /v1/listings/{id}`
- **Then** recibo `204`, el anuncio queda con `deleted_at` y `status = deleted`, y ya no aparece en ninguna lectura

**AC2 — Solo el autor o la administración (HU-09 AC3)**
- **Given** un anuncio de otro vecino
- **When** intento eliminarlo como miembro sin rol
- **Then** recibo `403`; como `community_admin` de esa comunidad, recibo `204`

**AC3 — Idempotencia visible**
- **Given** un anuncio ya eliminado
- **When** vuelvo a enviar `DELETE`
- **Then** recibo `404`

## 5. Plan de tareas

1. Filtro «no eliminado» por defecto en el repositorio de anuncios, con pruebas.
2. `DeleteListing` con reglas de permiso y pruebas unitarias.
3. Endpoint y pruebas de integración; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $OTRO"   # 403
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $AUTOR"  # 204
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $AUTOR"  # 404
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Ninguna consulta de anuncios devuelve anuncios eliminados.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Imágenes de anuncios eliminados:** se conservan en MinIO (el borrado es lógico). Una tarea posterior puede purgarlas tras un periodo de retención.
- **Restaurar un anuncio borrado por error:** no disponible en el MVP.
