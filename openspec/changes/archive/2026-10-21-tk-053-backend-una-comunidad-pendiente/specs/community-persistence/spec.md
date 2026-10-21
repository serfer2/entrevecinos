## ADDED Requirements

### Requirement: Una comunidad inactiva por creador
La base de datos MUST rechazar una segunda comunidad inactiva del mismo `created_by` mediante el índice único parcial `uq_community_one_pending_per_creator` (`WHERE NOT is_active`), y SHALL admitir varias comunidades activas del mismo creador. La migración `0007` SHALL ser reversible.

#### Scenario: Segunda inactiva
- **WHEN** se inserta una segunda comunidad inactiva del mismo creador
- **THEN** falla el índice `uq_community_one_pending_per_creator`
