# TK-053 · BD y backend: una sola comunidad pendiente por usuario

| Campo | Valor |
|---|---|
| **Tipo** | BD + Backend / funcionalidad |
| **Componente** | `apps/api/` (migración `0007`, área `communities`), `docs/api/` |
| **Historia** | HU-23 Tener una sola comunidad pendiente de aprobación a la vez (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-050, TK-052 |
| **Referencias** | `docs/api/paths/communities.yaml` (`post`), `components/responses/Conflict.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-050, un vecino puede crear tantas comunidades pendientes como quiera. HU-23 limita a una la comunidad pendiente de aprobación por usuario.

**Objetivo:** que `POST /communities` responda `409` si el usuario ya tiene una comunidad pendiente, y que la base de datos lo garantice también ante peticiones simultáneas.

## 2. Alcance

**Incluye**
- Migración `0007`: índice único parcial sobre `community(created_by)` para las comunidades inactivas.
- Comprobación en `CreateCommunity` y error de dominio `PendingCommunityExists` → `409`.
- Respuesta `409` de `createCommunity` en el contrato.

**No incluye**
- Retirar o editar la comunidad pendiente (sin historia; asumido).

## 3. Requisitos técnicos

### 3.1 Base de datos

- `0007`: `CREATE UNIQUE INDEX uq_community_one_pending_per_creator ON community (created_by) WHERE NOT is_active`, reflejado en `CommunityModel.__table_args__` (`postgresql_where`). `downgrade` elimina el índice.
- «Pendiente» = creada por el usuario e inactiva (asumido: en el MVP inactiva significa pendiente, TK-050 §8).
- Si una base de datos ya tuviera dos comunidades inactivas del mismo creador, la migración fallaría; las bases del MVP no las tienen porque hasta TK-050 todas eran activas.

### 3.2 Creación

- `CommunityRepository.has_pending(created_by) -> bool`.
- `CreateCommunity`: si la comunidad va a quedar pendiente (creador sin rol `platform_admin`) y `has_pending` es verdadero → `PendingCommunityExists`. Un `platform_admin` no queda limitado: sus comunidades nacen activas (TK-052).
- `add` crea la comunidad dentro de un *savepoint*; si otra petición simultánea gana la carrera, el `IntegrityError` del índice se traduce en `PendingCommunityExists`.
- Manejador: `PendingCommunityExists` → `409 {"detail": "Ya tienes una comunidad pendiente de aprobación."}`.

### 3.3 Contrato

- `communities.yaml` (`post`): respuesta `409` (`Conflict`) y frase en la descripción.
- `docs/api/README.md`: fila TK-053 en «Cambios».

### 3.4 Pruebas

- Caso de uso: segunda comunidad con una pendiente → error; tras aprobarla → se crea; `platform_admin` → sin límite.
- API: `409` con el mensaje; tras aprobar, `201`.
- BD: el índice impide dos comunidades inactivas del mismo creador y permite varias activas.

## 4. Criterios de aceptación

**AC1 — Con una comunidad pendiente (HU-23 AC1)**
- **Given** un usuario con una comunidad pendiente
- **When** hace `POST /v1/communities`
- **Then** recibe `409` con «Ya tienes una comunidad pendiente de aprobación.» y no se crea nada

**AC2 — Tras la aprobación (HU-23 AC2)**
- **Given** que su comunidad pendiente se ha aprobado
- **When** hace `POST /v1/communities`
- **Then** recibe `201` con `is_active: false`

**AC3 — Peticiones simultáneas**
- **Given** dos comunidades inactivas del mismo creador
- **When** se intenta guardar la segunda
- **Then** la base de datos la rechaza

## 5. Plan de tareas

1. Migración `0007` e índice en el modelo.
2. `has_pending`, `PendingCommunityExists`, comprobación en `CreateCommunity` y traducción del `IntegrityError`.
3. Manejador `409`, contrato y `docs/api/README.md`.
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev   # aplica la migración 0007
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# Vecino con una comunidad pendiente: POST /v1/communities → 409
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Las pruebas de la API y el lint pasan; la migración se aplica y se revierte.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Sin rechazo ni retirada:** si el `platform_admin` no aprueba la comunidad, el vecino no puede crear otra (ver TK-050 §8).
