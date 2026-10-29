# TK-074 · Documentación: alcance del MVP en el contrato de la API

| Campo | Valor |
|---|---|
| **Tipo** | Documentación / contrato |
| **Componente** | `docs/api/` (`openapi.yaml`, `paths/*.yaml`, `README.md`) |
| **Historia** | HU-34 Distinguir qué parte del modelo de datos y de la API pertenece al MVP (Épica 12) |
| **Prioridad** | Media |
| **Depende de** | — |
| **Referencias** | `readme.md` §1.2 (MVP) y §3 (modelo de datos); `apps/api/src/entrevecinos/presentation/v1/` (rutas implementadas); TK-050 (`x-mvp` de la administración de comunidades) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El contrato usa la extensión `x-mvp` para separar el MVP de las versiones futuras, pero no coincide con lo implementado:

| | Operaciones |
|---|---|
| Contrato (`docs/api/`) | 59 |
| Marcadas `x-mvp: true` | 33 |
| Implementadas en la API (`/v1`) | 27 |
| Marcadas `x-mvp: true` y **no implementadas** | 6 |

Las 6 operaciones marcadas como MVP sin implementar son de entidades del MVP, pero no las usa ninguna historia:

| Operación | `operationId` |
|---|---|
| `DELETE /users/me` | `deleteCurrentUser` |
| `GET /users/me/listings` | `listMyListings` |
| `POST /categories` | `createCategory` |
| `PATCH /categories/{category_id}` | `updateCategory` |
| `PATCH /communities/{community_id}` | `updateCommunity` |
| `DELETE /media/{asset_id}` | `deleteMedia` |

Comparación entidades ↔ rutas (modelo de datos de `readme.md` §3, 15 entidades):

| Entidad | Tabla implementada | Rutas del contrato | Alcance |
|---|---|---|---|
| `user` | `users` | `/auth/register`, `/auth/token`, `/users/me`, `/users/me/memberships` | MVP |
| `email_verification` | Sí | `/auth/email-verification`, `/auth/email-verification/resend` | MVP |
| `community` | Sí | `/communities`, `/communities/{id}`, `/admin/communities`, `/admin/communities/{id}` | MVP |
| `community_membership` | Sí | `/communities/{id}/memberships`, `/communities/{id}/memberships/{user_id}` | MVP |
| `category` | Sí | `GET /categories` | MVP |
| `listing` | Sí | `/communities/{id}/listings`, `/listings/{id}`, `/listings/{id}/status` | MVP |
| `media_asset` | Sí | `POST /media`, `GET /media/{id}` | MVP |
| `listing_image` | Sí | `PUT /listings/{id}/images` | MVP |
| `conversation`, `message` | No | Mensajería (8 operaciones) | Futura |
| `notification` | No | Notificaciones (3) | Futura |
| `professional_profile`, `professional_service`, `professional_profile_image` | No | Perfil profesional (9) | Futura |
| `report` | No | Denuncias (4) | Futura |

`GET /health` no corresponde a ninguna entidad. `/admin/users` (`user`) es una operación futura sobre una entidad del MVP.

**Conclusión:** el contrato tiene más rutas que entidades implementadas; las que sobran son de las 7 entidades sin tabla (futuras) y de 8 operaciones futuras sobre entidades del MVP (las 6 de arriba y las 2 de `/admin/users`).

**Objetivo:** que `x-mvp` signifique exactamente «implementada en el MVP» y que el contrato lo explique.

## 2. Alcance

**Incluye**
- `x-mvp: false` en las 6 operaciones de la tabla anterior.
- `openapi.yaml`: definir `x-mvp` en `info.description` («`true`: implementada en el MVP; `false`: pendiente de una versión futura») y añadir «(versión futura)» a la descripción de los *tags* cuyas operaciones son todas futuras (Mensajería, Notificaciones, Perfil profesional, Denuncias).
- Descripción de cada operación futura: empieza por «**Versión futura:** no implementada en el MVP.».
- `docs/api/README.md`:
  - Convención `x-mvp` con la nueva definición.
  - «Resumen de endpoints» en dos tablas: «MVP (implementado)» y «Versiones futuras», con las mismas filas por grupo; los grupos mixtos (Usuarios, Categorías, Comunidades, Media, Administración) aparecen en ambas.
  - Fila en «Cambios»: TK-074, `x-mvp: false` en las 6 operaciones.
- Lint (`redocly lint`) y bundle sin errores.

**No incluye**
- Implementar las 6 operaciones ni borrarlas del contrato.
- El `readme.md` (TK-075) y la prueba automática (TK-076).

## 3. Requisitos técnicos

- Las operaciones futuras se conservan: el contrato documenta también lo que está por venir.
- No cambian esquemas, rutas ni respuestas; solo `x-mvp` y textos.
- `x-mvp` es obligatorio en todas las operaciones (asumido: ya lo está; se comprueba).

## 4. Criterios de aceptación

**AC1 — Marca exacta (HU-34 AC2)**
- **Given** el contrato actualizado
- **When** cuento las operaciones con `x-mvp: true`
- **Then** son 27 y coinciden con las rutas de `apps/api/src/entrevecinos/presentation/v1/`

**AC2 — Futuras explícitas (HU-34 AC1)**
- **Given** una operación con `x-mvp: false`
- **When** la abro en la previsualización del contrato
- **Then** su descripción empieza por «Versión futura» y, si su grupo es entero futuro, el *tag* lo indica

**AC3 — Resumen (HU-34 AC3)**
- **Given** `docs/api/README.md`
- **When** leo el resumen de endpoints
- **Then** veo por separado las operaciones del MVP y las de versiones futuras

## 5. Plan de tareas

1. `x-mvp: false` y «Versión futura» en las operaciones afectadas.
2. `info.description` y *tags* de `openapi.yaml`.
3. `docs/api/README.md` (convención, resumen y cambios).
4. Lint y bundle.

## 6. Verificación

```bash
cd docs/api
npx @redocly/cli lint openapi.yaml
npx @redocly/cli bundle openapi.yaml -o dist/openapi.bundled.yaml
grep -c "x-mvp: true" paths/*.yaml | awk -F: '{s+=$2} END {print s}'   # 27
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Lint del contrato sin errores.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Las 6 operaciones sin implementar pasan a futuras.** Alternativa: implementarlas en el MVP. Ninguna historia del MVP las necesita (borrar la cuenta, «mis anuncios», gestionar categorías, editar la comunidad, borrar una imagen suelta), así que se recomienda marcarlas como futuras.
- **Cambio de significado de `x-mvp`:** antes era «previsto para el MVP»; ahora es «implementado en el MVP». TK-076 lo hace cumplir.
