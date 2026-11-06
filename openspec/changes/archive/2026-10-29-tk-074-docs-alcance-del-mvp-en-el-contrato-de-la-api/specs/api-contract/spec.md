## ADDED Requirements

### Requirement: Alcance del MVP en el contrato
Cada operación de `docs/api/` SHALL declarar `x-mvp`: `true` si está implementada en el MVP y `false` si queda para una versión futura. Las operaciones `x-mvp: false` SHALL empezar su descripción por «**Versión futura:** no implementada en el MVP.», y los *tags* cuyas operaciones son todas futuras SHALL indicarlo. `docs/api/README.md` MUST resumir por separado las operaciones del MVP y las de versiones futuras.

#### Scenario: Operación del MVP
- **WHEN** se consulta `listCommunityListings` en el contrato
- **THEN** tiene `x-mvp: true` y está implementada en `/v1/communities/{community_id}/listings`

#### Scenario: Operación futura de una entidad del MVP
- **WHEN** se consulta `deleteCurrentUser`
- **THEN** tiene `x-mvp: false` y su descripción empieza por «Versión futura»

#### Scenario: Grupo futuro
- **WHEN** se previsualiza el contrato
- **THEN** los *tags* Mensajería, Notificaciones, Perfil profesional y Denuncias indican «(versión futura)»
