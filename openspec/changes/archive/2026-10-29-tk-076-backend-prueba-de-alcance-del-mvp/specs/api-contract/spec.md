## ADDED Requirements

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
