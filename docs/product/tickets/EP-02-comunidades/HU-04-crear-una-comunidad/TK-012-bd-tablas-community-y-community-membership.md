# TK-012 · Base de datos: tablas `community` y `community_membership`

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos |
| **Componente** | `apps/api/` (`infrastructure/db/models/`, `migrations/`) |
| **Historia** | HU-04 Crear una comunidad (Épica 2) |
| **Prioridad** | Alta (bloquea toda la Épica 2 y las siguientes) |
| **Depende de** | TK-005 |
| **Referencias** | `readme.md` §3.2 (`community`, `community_membership`, enums `membership_role` y `membership_status`, índices recomendados); `docs/api/components/schemas/Community.yaml`, `Membership.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Las comunidades y la pertenencia de los usuarios a ellas son la base del control de acceso de todo el producto: solo los miembros aprobados ven y publican anuncios. Todavía no existen en la base de datos.

**Objetivo:** crear la migración `0002` con los enums `membership_role` y `membership_status`, y las tablas `community` y `community_membership`, siguiendo el modelo de datos y las convenciones de TK-005.

## 2. Alcance

**Incluye**
- Modelos ORM `CommunityModel` y `CommunityMembershipModel`.
- Migración `0002_create_community` reversible.
- Índices recomendados por el README para membresías.
- Pruebas de restricciones y valores por defecto.

**No incluye**
- Dominio, casos de uso y endpoints (TK-013, TK-015, TK-017).
- Búsqueda avanzada (trigramas) de comunidades: el MVP usa `ILIKE` (ver TK-015).

## 3. Requisitos técnicos

### 3.1 Nombres de tabla

En singular, igual que las entidades del modelo de datos: `community` y `community_membership`. La única excepción es `users` (TK-005), porque `user` es una palabra reservada de PostgreSQL (ver `readme.md` §3.2).

### 3.2 Tabla `community`

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `UUID` | PK, `DEFAULT gen_random_uuid()` |
| `name` | `VARCHAR(120)` | `NOT NULL`, `CHECK (length(trim(name)) > 0)` |
| `description` | `TEXT` | `NULL` |
| `postal_code` | `VARCHAR(16)` | `NULL` |
| `city` | `VARCHAR(120)` | `NULL` |
| `created_by` | `UUID` | `NOT NULL`, FK → `users.id` (`ON DELETE RESTRICT`) |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()`, `onupdate=statement_timestamp()` |

- El nombre **no** es único: puede haber dos «Urbanización Los Olivos» en ciudades distintas (asumido).

### 3.3 Tabla `community_membership`

| Columna | Tipo | Restricciones |
|---|---|---|
| `community_id` | `UUID` | PK compuesta, FK → `community.id` (`ON DELETE CASCADE`) |
| `user_id` | `UUID` | PK compuesta, FK → `users.id` (`ON DELETE CASCADE`) |
| `role` | `membership_role` | `NOT NULL`, `DEFAULT 'member'` |
| `status` | `membership_status` | `NOT NULL`, `DEFAULT 'pending'` |
| `reviewed_by` | `UUID` | `NULL`, FK → `users.id` (`ON DELETE SET NULL`) |
| `requested_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |
| `reviewed_at` | `TIMESTAMPTZ` | `NULL` |
| `joined_at` | `TIMESTAMPTZ` | `NULL` |

- Enums: `membership_role` (`member`, `community_admin`, `moderator`) y `membership_status` (`pending`, `approved`, `rejected`, `blocked`).
- `CHECK (status <> 'approved' OR joined_at IS NOT NULL)`: una membresía aprobada siempre tiene fecha de entrada (asumido).
- Índices: `ix_community_membership_user_id_status (user_id, status)` y `ix_community_membership_community_id_status (community_id, status)`.
- Los usuarios se borran de forma lógica (`deleted_at`), así que los `CASCADE` solo actúan en borrados físicos (pruebas o mantenimiento).

### 3.4 Pruebas (`@pytest.mark.db`)

- Inserción mínima de comunidad y de membresía con los valores por defecto.
- PK compuesta: una segunda membresía del mismo usuario en la misma comunidad falla.
- `CHECK` del nombre en blanco y de `approved` sin `joined_at`.
- `alembic check` sin diferencias y `downgrade`/`upgrade` reversibles (la prueba de TK-005 cubre todas las migraciones).

## 4. Criterios de aceptación

**AC1 — Migración aplicada**
- **Given** el entorno levantado con `make dev`
- **When** consulto `\d community` y `\d community_membership`
- **Then** existen con las columnas, restricciones, claves foráneas e índices de §3, y `alembic current` muestra `0002 (head)`

**AC2 — Una membresía por usuario y comunidad**
- **Given** una membresía de un usuario en una comunidad
- **When** inserto otra para el mismo par
- **Then** la base de datos la rechaza por la clave primaria

**AC3 — Integridad**
- **Given** una membresía `approved` sin `joined_at`, o una comunidad con nombre `"  "`
- **When** la inserto
- **Then** la base de datos la rechaza

**AC4 — Reversible**
- **Given** la base de datos en `0002`
- **When** ejecuto `alembic downgrade 0001` y `alembic upgrade head`
- **Then** ambos terminan sin errores y la tabla `users` conserva sus datos

## 5. Plan de tareas

1. Modelos ORM y registro en `models/__init__.py`.
2. Migración `0002` (enums, tablas, índices) con `downgrade()`.
3. Pruebas de §3.4 y `alembic check`.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec db psql -U entrevecinos -c '\d community' -c '\d community_membership'
$COMPOSE run --rm api alembic downgrade 0001 && $COMPOSE run --rm api alembic upgrade head
$COMPOSE run --rm api alembic check
$COMPOSE run --rm api pytest -m db
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `pytest`, `ruff check` y `alembic check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Nombres en plural:** igual que `users`; conviene reflejarlo en `readme.md` §3.
- **Comunidades desactivadas (`is_active = false`):** no hay historia que las desactive en el MVP; el campo queda preparado.
