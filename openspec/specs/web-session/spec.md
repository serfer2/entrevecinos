# web-session Specification

## Purpose
Inicio de sesión desde el navegador (`/iniciar-sesion`) y protección de las rutas privadas (proxy + DAL).
## Requirements
### Requirement: Inicio de sesión desde el navegador
`/iniciar-sesion` SHALL permitir iniciar sesión con correo y contraseña; si son correctos, guarda `ev_session` y redirige a `next` (si es una ruta interna segura) o a `/inicio`, que saluda al usuario por su nombre.

#### Scenario: Acceso correcto
- **WHEN** se envían credenciales correctas
- **THEN** el navegador queda en `/inicio` con «Hola, {nombre}»

### Requirement: Error genérico
Con credenciales incorrectas el formulario SHALL mostrar «Correo o contraseña incorrectos.» sin marcar ningún campo y conservando el correo.

#### Scenario: Credenciales incorrectas
- **WHEN** se envía un correo no registrado o una contraseña incorrecta
- **THEN** se muestra el mismo mensaje en ambos casos

### Requirement: Rutas privadas por defecto
Toda ruta salvo `/`, `/registro` e `/iniciar-sesion` MUST redirigir a `/iniciar-sesion?next=<ruta>` cuando no existe la *cookie* `ev_session`.

#### Scenario: Acceso sin sesión
- **WHEN** se abre `/comunidades/123/anuncios` sin sesión
- **THEN** se redirige a `/iniciar-sesion?next=%2Fcomunidades%2F123%2Fanuncios` y, tras iniciar sesión, se vuelve a esa ruta

### Requirement: Sesión caducada sin bucles
Con una *cookie* cuyo token no es válido, las páginas privadas SHALL redirigir a `/iniciar-sesion?motivo=sesion-caducada`, que muestra el formulario con un aviso, sin bucles de redirección.

#### Scenario: Token inválido
- **WHEN** `ev_session` contiene un token no válido y se abre `/inicio`
- **THEN** se muestra `/iniciar-sesion` con «Tu sesión ha caducado. Vuelve a iniciar sesión.»

### Requirement: Redirección segura
El parámetro `next` MUST ignorarse si no es una ruta interna.

#### Scenario: next externo
- **WHEN** se inicia sesión desde `/iniciar-sesion?next=https://evil.example`
- **THEN** se redirige a `/inicio`

### Requirement: Raíz según la sesión
`/` SHALL redirigir a `/inicio` cuando el usuario tiene una sesión válida y a `/iniciar-sesion` cuando no la tiene, su token no es válido o la API no responde, sin bucles de redirección.

#### Scenario: Sin sesión
- **WHEN** se abre `/` sin la *cookie* `ev_session`
- **THEN** se redirige a `/iniciar-sesion`, cuyo formulario enlaza con `/registro`

#### Scenario: Con sesión
- **WHEN** se abre `/` con una sesión válida
- **THEN** se redirige a `/inicio`

#### Scenario: API caída
- **WHEN** se abre `/` con una *cookie* `ev_session` y la API no responde
- **THEN** se redirige a `/iniciar-sesion`

