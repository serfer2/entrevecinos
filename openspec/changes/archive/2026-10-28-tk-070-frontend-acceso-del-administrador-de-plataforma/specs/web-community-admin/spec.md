## MODIFIED Requirements

### Requirement: Permiso restringido
El enlace «Gestionar comunidad» SHALL mostrarse solo a `community_admin` aprobado y a `platform_admin`, y la página MUST mostrar «No tienes permisos para gestionar esta comunidad.» cuando la API responde `403`.

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol escribe la URL de gestión
- **THEN** ve el aviso de permisos

#### Scenario: Administrador de plataforma
- **WHEN** un `platform_admin` sin membresía abre la comunidad
- **THEN** ve «Gestionar comunidad»
