# community-persistence Specification

## Purpose
Esquema de comunidades y membresías (tablas `community` y `community_membership`).
## Requirements
### Requirement: Tablas de comunidades y membresías
La migración `0002` SHALL crear `community` y `community_membership` con los enums `membership_role` (`member`, `community_admin`, `moderator`) y `membership_status` (`pending`, `approved`, `rejected`, `blocked`), y los índices `(user_id, status)` y `(community_id, status)` sobre las membresías.

#### Scenario: Valores por defecto
- **WHEN** se inserta una comunidad y una membresía con los campos mínimos
- **THEN** la comunidad queda activa y la membresía con `role = member`, `status = pending` y `requested_at` informado

### Requirement: Una membresía por usuario y comunidad
La base de datos MUST rechazar una segunda membresía del mismo usuario en la misma comunidad.

#### Scenario: Duplicado
- **WHEN** se inserta otra membresía para el mismo par
- **THEN** falla por la clave primaria

### Requirement: Integridad
La base de datos MUST rechazar una comunidad con nombre en blanco y una membresía `approved` sin `joined_at`.

#### Scenario: Aprobada sin fecha de entrada
- **WHEN** se inserta una membresía `approved` con `joined_at` nulo
- **THEN** falla la restricción `CHECK`

### Requirement: Migración reversible
`alembic downgrade 0001` SHALL eliminar las tablas y los enums, y `upgrade head` volver a crearlos.

#### Scenario: Ida y vuelta
- **WHEN** se baja a `0001` y se sube a `head`
- **THEN** ambos terminan sin errores

### Requirement: Una comunidad inactiva por creador
La base de datos MUST rechazar una segunda comunidad inactiva del mismo `created_by` mediante el índice único parcial `uq_community_one_pending_per_creator` (`WHERE NOT is_active`), y SHALL admitir varias comunidades activas del mismo creador. La migración `0007` SHALL ser reversible.

#### Scenario: Segunda inactiva
- **WHEN** se inserta una segunda comunidad inactiva del mismo creador
- **THEN** falla el índice `uq_community_one_pending_per_creator`

