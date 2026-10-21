## MODIFIED Requirements

### Requirement: Inicio de sesión desde el navegador
`/iniciar-sesion` SHALL permitir iniciar sesión con correo y contraseña; si son correctos, guarda `ev_session` y redirige a `next` (si es una ruta interna segura) o, sin él, a `/comunidades` cuando el usuario no es miembro aprobado de ninguna comunidad activa y a `/inicio` en otro caso o si la API no responde. `/inicio` saluda al usuario por su nombre.

#### Scenario: Acceso correcto
- **WHEN** un miembro aprobado de alguna comunidad envía credenciales correctas
- **THEN** el navegador queda en `/inicio` con «Hola, {nombre}»

#### Scenario: Sin comunidades
- **WHEN** un usuario sin membresías aprobadas, o solo con solicitudes pendientes, envía credenciales correctas
- **THEN** el navegador queda en `/comunidades`

#### Scenario: Destino solicitado
- **WHEN** un usuario sin comunidades inicia sesión desde `/iniciar-sesion?next=%2Fperfil`
- **THEN** el navegador queda en `/perfil`
