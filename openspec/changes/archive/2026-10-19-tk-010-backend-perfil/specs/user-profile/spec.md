## ADDED Requirements

### Requirement: Edición del perfil propio
`PATCH /v1/users/me` SHALL actualizar solo los campos enviados (`full_name`, `phone`) del usuario autenticado y responder `200` con el `User` actualizado.

#### Scenario: Nombre y teléfono
- **WHEN** se envía `{"full_name": "Alex Vecino García", "phone": "+34 600 111 222"}`
- **THEN** la respuesta es `200` y `GET /v1/users/me` devuelve los mismos valores

#### Scenario: Actualización parcial
- **WHEN** se envía solo `full_name`, y después `{"phone": null}`
- **THEN** el primer cambio no toca el teléfono y el segundo lo borra sin tocar el nombre

### Requirement: Nombre obligatorio
El nombre MUST NOT quedar vacío: `""`, solo espacios o `null` SHALL responder `422` con `loc` `["body", "full_name"]` sin modificar los datos.

#### Scenario: Nombre en blanco
- **WHEN** se envía `{"full_name": "   "}`
- **THEN** la respuesta es `422` y el nombre guardado no cambia

### Requirement: Campos permitidos
El endpoint MUST responder `422` sin modificar nada ante un cuerpo vacío, un teléfono que no cumple `^\+?[0-9 ()-]{6,32}$`, o campos distintos de `full_name` y `phone`.

#### Scenario: Campo no permitido
- **WHEN** se envía `email`, `platform_role` o `password`
- **THEN** la respuesta es `422`

### Requirement: Solo el perfil propio
El endpoint SHALL modificar únicamente al usuario del token y MUST responder `401` sin token.

#### Scenario: Dos usuarios
- **WHEN** A actualiza su perfil
- **THEN** los datos de B no cambian
