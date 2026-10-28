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

### Requirement: Gestión de miembros
La gestión de la comunidad SHALL tener las pestañas «Solicitudes» y «Miembros». `/comunidades/<id>/gestion/miembros` MUST listar los miembros con su rol y estado, filtrables por estado, con «Bloquear» y «Expulsar» (con confirmación) y «Desbloquear» según la fila; tras cada acción se muestra «<nombre> ha sido bloqueado/desbloqueado/expulsado.» o el motivo del rechazo.

#### Scenario: Bloquear
- **WHEN** el administrador bloquea a un miembro y confirma
- **THEN** ve «<nombre> ha sido bloqueado.» y ese vecino deja de ver los anuncios de la comunidad

#### Scenario: Sin permisos
- **WHEN** un miembro sin rol abre la URL de gestión de miembros
- **THEN** ve «No tienes permisos para gestionar esta comunidad.»

### Requirement: Ocultar y restaurar anuncios desde el detalle
Los gestores de la comunidad SHALL ver «Ocultar anuncio» (con confirmación) en un anuncio visible y «Restaurar anuncio» en uno oculto; al ocultar vuelven al listado con «Anuncio ocultado.» y el anuncio deja de aparecer. El autor y los gestores ven en un anuncio oculto «Este anuncio está oculto y no se muestra en la comunidad.»; a un miembro sin rol MUST NOT ofrecérsele la ocultación.

#### Scenario: Ocultación
- **WHEN** un administrador pulsa «Ocultar anuncio» y confirma
- **THEN** vuelve al listado con «Anuncio ocultado.» y el anuncio ya no aparece

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol abre el anuncio de otro vecino
- **THEN** no ve «Ocultar anuncio»

