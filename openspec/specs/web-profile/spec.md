# web-profile Specification

## Purpose
Consulta y edición del perfil propio desde el navegador (`/perfil`).
## Requirements
### Requirement: Consulta del perfil
`/perfil` SHALL mostrar el nombre, el correo (no editable) y el teléfono del usuario de la sesión, o el teléfono vacío si no tiene.

#### Scenario: Abrir el perfil
- **WHEN** un usuario con sesión abre `/perfil` desde el enlace de `/inicio`
- **THEN** ve sus datos guardados y un formulario con el nombre y el teléfono

### Requirement: Edición del perfil
Al guardar, el formulario SHALL enviar el nombre y el teléfono (`null` si está vacío) y mostrar «Perfil actualizado.» con los datos nuevos.

#### Scenario: Guardar cambios
- **WHEN** se cambia el nombre o el teléfono y se pulsa «Guardar cambios»
- **THEN** se muestra «Perfil actualizado.» y `/inicio` saluda con el nombre nuevo

#### Scenario: Borrar el teléfono
- **WHEN** se vacía el teléfono y se guarda
- **THEN** el teléfono se elimina

### Requirement: Nombre obligatorio
Con el nombre vacío o solo con espacios, la acción MUST NOT llamar a la API y SHALL mostrar «El nombre es obligatorio.» bajo el campo, sin cambiar los datos guardados.

#### Scenario: Nombre en blanco
- **WHEN** se guarda con el nombre `"   "` sin validación del navegador
- **THEN** se muestra el error y, al recargar, el nombre anterior sigue guardado

### Requirement: Sesión requerida
`/perfil` y su acción MUST exigir una sesión válida.

#### Scenario: Sin sesión
- **WHEN** se abre `/perfil` sin sesión
- **THEN** se redirige a `/iniciar-sesion?next=%2Fperfil`

