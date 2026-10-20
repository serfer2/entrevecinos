# web-community-admin Specification

## Purpose
Gestión de la comunidad desde la interfaz (solicitudes, miembros y moderación).
## Requirements
### Requirement: Ver solicitudes pendientes
`/comunidades/<id>/gestion/solicitudes` SHALL mostrar al administrador las solicitudes pendientes, paginadas, con el nombre del solicitante y la fecha de solicitud, o «No hay solicitudes pendientes.».

#### Scenario: Con solicitudes
- **WHEN** el administrador abre «Gestionar comunidad»
- **THEN** ve cada solicitud con su nombre y los botones «Aprobar» y «Rechazar»

### Requirement: Aprobar o rechazar
«Aprobar» SHALL aprobar la solicitud y mostrar «Solicitud aprobada.»; «Rechazar», tras confirmar, SHALL rechazarla y mostrar «Solicitud rechazada.». Si ya estaba revisada se MUST mostrar «Esta solicitud ya se había revisado.».

#### Scenario: Aprobar
- **WHEN** el administrador pulsa «Aprobar»
- **THEN** la solicitud desaparece de la lista y el solicitante ve «Entrar» en su búsqueda

### Requirement: Permiso restringido
El enlace «Gestionar comunidad» SHALL mostrarse solo a `community_admin`, y la página MUST mostrar «No tienes permisos para gestionar esta comunidad.» cuando la API responde `403`.

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol escribe la URL de gestión
- **THEN** ve el aviso de permisos

