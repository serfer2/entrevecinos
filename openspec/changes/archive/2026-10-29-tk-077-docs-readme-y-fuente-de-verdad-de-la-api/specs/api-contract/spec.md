## ADDED Requirements

### Requirement: Fuente de verdad del contrato
`docs/api/openapi.yaml` SHALL ser la única fuente de verdad del contrato de la API. `readme.md` §4 MUST remitir a él y a `docs/api/README.md`, y cualquier fragmento de OpenAPI que incluya SHALL ser un extracto del contrato *bundled*, idéntico en rutas, parámetros, cuerpos, respuestas y esquemas, con el aviso de que prevalece el contrato.

#### Scenario: Enlace
- **WHEN** se lee `readme.md` §4
- **THEN** remite a `docs/api/openapi.yaml` como fuente de verdad

#### Scenario: Extracto coherente
- **WHEN** se compara `registerUser` del extracto con la del bundle
- **THEN** son idénticas, incluida la respuesta `201` con `RegistrationResponse`
