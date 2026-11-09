## MODIFIED Requirements

### Requirement: Gestión de miembros
La gestión de la comunidad SHALL tener las pestañas «Solicitudes» y «Miembros». `/comunidades/<id>/gestion/miembros` MUST listar los miembros con su rol y estado, filtrables por estado, con «Bloquear» y «Expulsar» (con confirmación) y «Desbloquear» según la fila; tras cada acción se muestra «<nombre> ha sido bloqueado/desbloqueado/expulsado.» o el motivo del rechazo. Solo para un `platform_admin`, la página SHALL ofrecer además, con confirmación, «Nombrar administrador» en cada miembro aprobado que no es administrador y «Quitar administrador» en cada administrador aprobado (incluido él mismo), con los mensajes «<nombre> ha sido nombrado administrador.» y «<nombre> ya no es administrador.»; si la API responde `409`, MUST mostrarse su motivo («La comunidad debe tener al menos un administrador.» o «Solo se puede cambiar el rol de un miembro aprobado.»). Un `community_admin` MUST NOT ver estas dos acciones.

#### Scenario: Bloquear
- **WHEN** el administrador bloquea a un miembro y confirma
- **THEN** ve «<nombre> ha sido bloqueado.» y ese vecino deja de ver los anuncios de la comunidad

#### Scenario: Sin permisos
- **WHEN** un miembro sin rol abre la URL de gestión de miembros
- **THEN** ve «No tienes permisos para gestionar esta comunidad.»

#### Scenario: Nombrar administrador
- **WHEN** un `platform_admin` pulsa «Nombrar administrador» en un miembro aprobado y confirma
- **THEN** ve «<nombre> ha sido nombrado administrador.» y la fila muestra el rol «Administrador»

#### Scenario: Último administrador
- **WHEN** un `platform_admin` quita el rol al único administrador y confirma
- **THEN** ve «La comunidad debe tener al menos un administrador.»

#### Scenario: Administrador de comunidad
- **WHEN** un `community_admin` abre «Miembros»
- **THEN** no ve «Nombrar administrador» ni «Quitar administrador»
