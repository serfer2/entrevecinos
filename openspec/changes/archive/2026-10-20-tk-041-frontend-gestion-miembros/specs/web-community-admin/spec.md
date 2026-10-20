## ADDED Requirements

### Requirement: Gestión de miembros
La gestión de la comunidad SHALL tener las pestañas «Solicitudes» y «Miembros». `/comunidades/<id>/gestion/miembros` MUST listar los miembros con su rol y estado, filtrables por estado, con «Bloquear» y «Expulsar» (con confirmación) y «Desbloquear» según la fila; tras cada acción se muestra «<nombre> ha sido bloqueado/desbloqueado/expulsado.» o el motivo del rechazo.

#### Scenario: Bloquear
- **WHEN** el administrador bloquea a un miembro y confirma
- **THEN** ve «<nombre> ha sido bloqueado.» y ese vecino deja de ver los anuncios de la comunidad

#### Scenario: Sin permisos
- **WHEN** un miembro sin rol abre la URL de gestión de miembros
- **THEN** ve «No tienes permisos para gestionar esta comunidad.»
