# community-management Specification

## Purpose
Creación y consulta de comunidades (`POST /v1/communities`, `GET /v1/communities/{id}`).
## Requirements
### Requirement: Crear una comunidad
`POST /v1/communities` SHALL crear la comunidad del usuario autenticado y registrarlo como `community_admin` con membresía `approved` y `joined_at`, respondiendo `201` con el esquema `Community`.

#### Scenario: Creación correcta
- **WHEN** un usuario autenticado envía `{"name": "Urbanización Los Olivos", "city": "Majadahonda", "postal_code": "28220"}`
- **THEN** recibe `201` con `created_by` igual a su id y existe su membresía `community_admin`/`approved`

### Requirement: Validación de la comunidad
`name` MUST tener de 1 a 120 caracteres tras recortar espacios; `description` (máximo 2000), `postal_code` (16) y `city` (120) son opcionales y `""` equivale a `null`. Datos inválidos SHALL responder `422` sin crear nada.

#### Scenario: Nombre en blanco
- **WHEN** se envía `{"name": "  "}` o no se envía `name`
- **THEN** la respuesta es `422` con `loc` `["body", "name"]` y no se crea ni la comunidad ni la membresía

### Requirement: Consultar una comunidad
`GET /v1/communities/{community_id}` SHALL devolver una comunidad activa a cualquier usuario autenticado y `404 {"detail": "Recurso no encontrado."}` si no existe o está desactivada.

#### Scenario: Inexistente
- **WHEN** se consulta un id que no existe
- **THEN** la respuesta es `404`

### Requirement: Autenticación obligatoria
Ambos endpoints MUST responder `401` sin token.

#### Scenario: Sin token
- **WHEN** se llama sin `Authorization`
- **THEN** la respuesta es `401`

