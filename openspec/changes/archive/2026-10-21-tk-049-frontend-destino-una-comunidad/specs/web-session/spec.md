## MODIFIED Requirements

### Requirement: Inicio de sesión desde el navegador
`/iniciar-sesion` SHALL permitir iniciar sesión con correo y contraseña; si son correctos, guarda `ev_session` y redirige a `next` (si es una ruta interna segura) o, sin él, según las comunidades activas en las que el usuario es miembro aprobado: ninguna → `/comunidades`; una → `/comunidades/{id}`; varias, o si la API no responde → `/inicio`. `/inicio` saluda al usuario por su nombre.

#### Scenario: Acceso correcto
- **WHEN** un miembro aprobado de varias comunidades envía credenciales correctas
- **THEN** el navegador queda en `/inicio` con «Hola, {nombre}»

#### Scenario: Sin comunidades
- **WHEN** un usuario sin membresías aprobadas, o solo con solicitudes pendientes, envía credenciales correctas
- **THEN** el navegador queda en `/comunidades`

#### Scenario: Una comunidad
- **WHEN** un usuario aprobado en una sola comunidad activa, aunque tenga solicitudes pendientes en otras, envía credenciales correctas
- **THEN** el navegador queda en `/comunidades/{id}` de esa comunidad

#### Scenario: Destino solicitado
- **WHEN** un usuario sin comunidades inicia sesión desde `/iniciar-sesion?next=%2Fperfil`
- **THEN** el navegador queda en `/perfil`
