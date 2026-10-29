# api-contract Specification

## Purpose
Contrato de la API en `docs/api/`: alcance del MVP, comprobación automática y fuente de verdad.
## Requirements
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

### Requirement: Comprobación automática del alcance del MVP
Las pruebas de la API SHALL comparar las operaciones implementadas (método y ruta, sin el prefijo `/v1`) con las marcadas `x-mvp: true` en `docs/api/` y MUST fallar si difieren, nombrando las operaciones sobrantes de cada lado. Sin el contrato disponible, la prueba SHALL omitirse.

#### Scenario: Coinciden
- **WHEN** se ejecutan las pruebas con la API y el contrato alineados
- **THEN** la prueba pasa

#### Scenario: Endpoint sin contrato
- **WHEN** se añade un endpoint a la API sin `x-mvp: true` en el contrato
- **THEN** la prueba falla y nombra el endpoint

#### Scenario: MVP sin implementar
- **WHEN** el contrato marca `x-mvp: true` una operación que la API no implementa
- **THEN** la prueba falla y nombra la operación
