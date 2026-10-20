# TK-013 · Backend: crear y consultar una comunidad (`POST /v1/communities`, `GET /v1/communities/{id}`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `communities`) |
| **Historia** | HU-04 Crear una comunidad (Épica 2) |
| **Prioridad** | Alta |
| **Depende de** | TK-008, TK-012 |
| **Referencias** | `docs/api/paths/communities.yaml` (`post`), `communities_community_id.yaml` (`get`); esquemas `CommunityCreate`, `Community`; `components/responses/NotFound.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-04 pide que un vecino cree la comunidad de su barrio y quede como su administrador con acceso aprobado. El contrato define `POST /communities` (el creador queda como `community_admin` con membresía `approved`) y `GET /communities/{id}`.

**Objetivo:** implementar ambos endpoints con la arquitectura limpia de la Épica 1, y añadir el manejo común del error `404`.

## 2. Alcance

**Incluye**
- Dominio `communities`: entidades `Community`, `NewCommunity`, `Membership`, enums `MembershipRole` y `MembershipStatus`, error `CommunityNotFound`.
- Puerto `CommunityRepository` y casos de uso `CreateCommunity` y `GetCommunity`.
- Repositorio SQLAlchemy y endpoints.
- Manejador común de errores «no encontrado» → `404 {"detail": "Recurso no encontrado."}`.

**No incluye**
- Búsqueda de comunidades y solicitudes de acceso (TK-015).
- `PATCH /communities/{id}`: no hay historia que lo pida en el MVP.
- Comprobación de roles por comunidad (TK-017).

## 3. Requisitos técnicos

### 3.1 Diseño por capas

```
domain/communities/
├── entities.py      # Community, NewCommunity, Membership, MembershipRole, MembershipStatus
└── errors.py        # CommunityNotFound
application/communities/
├── ports.py         # CommunityRepository
├── create_community.py
└── get_community.py
infrastructure/communities/sqlalchemy_community_repository.py
presentation/v1/
├── communities.py
└── schemas/communities.py   # CommunityCreateRequest, CommunityResponse
```

- `CommunityRepository.add(community: NewCommunity, admin_id) -> Community`: inserta la comunidad **y** la membresía del creador (`role = community_admin`, `status = approved`, `joined_at = reviewed_at = now()`, `reviewed_by = creador`) en la misma transacción.
- `CommunityRepository.get(community_id) -> Community | None`: solo comunidades activas (`is_active = true`).
- Los errores de dominio «no encontrado» heredan de una base común `NotFoundError` (en `domain/errors.py`), que la presentación traduce a `404`. TK-015 y siguientes reutilizan esta base.

### 3.2 `POST /v1/communities` (autenticado)

- **Petición** (`CommunityCreateRequest`, `extra="forbid"`):
  - `name`: se recortan los espacios; de 1 a 120 caracteres.
  - `description`: opcional; se recorta; `""` → `null`; máximo 2000 caracteres (`maxLength: 2000` en `CommunityCreate.yaml` y `CommunityUpdate.yaml`).
  - `postal_code`: opcional; se recorta; `""` → `null`; máximo 16.
  - `city`: opcional; se recorta; `""` → `null`; máximo 120.
- **201**: `Community` (`id`, `name`, `description`, `postal_code`, `city`, `created_by`, `is_active`, `created_at`).
- **401** sin sesión; **422** con datos inválidos (formato de TK-006).

### 3.3 `GET /v1/communities/{community_id}` (autenticado)

- **200**: `Community`. Los datos básicos son visibles para cualquier usuario autenticado, para poder solicitar el acceso.
- **404**: id inexistente o comunidad desactivada. Un `community_id` que no es UUID → **422**.

## 4. Criterios de aceptación

**AC1 — Creación correcta (HU-04 AC1)**
- **Given** que he iniciado sesión
- **When** envío `POST /v1/communities` con `{"name": "Urbanización Los Olivos", "city": "Majadahonda", "postal_code": "28220"}`
- **Then** recibo `201` con la comunidad (`created_by` = mi id) y en la base de datos tengo una membresía `community_admin` / `approved` con `joined_at`

**AC2 — Nombre obligatorio (HU-04 AC2)**
- **Given** que he iniciado sesión
- **When** envío un nombre vacío, solo con espacios o sin nombre
- **Then** recibo `422` con `loc` `["body", "name"]` y no se crea ni la comunidad ni la membresía

**AC3 — Consulta**
- **Given** una comunidad existente
- **When** cualquier usuario autenticado consulta `GET /v1/communities/{id}`
- **Then** recibe `200` con sus datos; con un id inexistente recibe `404 {"detail": "Recurso no encontrado."}`

**AC4 — Autenticación**
- **Given** que no envío token
- **When** llamo a cualquiera de los dos endpoints
- **Then** recibo `401` (TK-008)

## 5. Plan de tareas

1. Dominio (`communities`) y base `NotFoundError` con su manejador `404`.
2. Puerto, casos de uso y pruebas unitarias con un repositorio en memoria.
3. Repositorio SQLAlchemy (comunidad + membresía del creador en una transacción).
4. Esquemas y endpoints; comprobar que `/openapi.json` coincide con el contrato.
5. Pruebas de integración (AC1–AC4) y verificación según la sección 6.

## 6. Verificación

```bash
make dev
TOKEN=...   # POST /v1/auth/token
curl -s -X POST http://localhost:8000/v1/communities -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"name":"Urbanización Los Olivos","city":"Majadahonda"}'   # 201
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/v1/communities \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"name":"  "}'        # 422
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -c 'select role, status, joined_at is not null from community_membership;'
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan; los casos de uso tienen pruebas unitarias.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Comunidades duplicadas o falsas:** cualquier vecino puede crear comunidades. La moderación de comunidades corresponde al panel de `platform_admin`, fuera del MVP.
