## ADDED Requirements

### Requirement: Cerrar sesión
La cabecera de la zona privada SHALL mostrar, después de «Mi perfil», un botón «Cerrar sesión» que, mediante una petición `POST`, borra la *cookie* `ev_session` y redirige a `/` (que lleva a `/iniciar-sesion`). Tras cerrar la sesión, las páginas privadas MUST redirigir al inicio de sesión, también al volver con «Atrás».

#### Scenario: Cierre de sesión
- **WHEN** un usuario con sesión pulsa «Cerrar sesión»
- **THEN** la *cookie* `ev_session` desaparece y el navegador queda en `/iniciar-sesion`

#### Scenario: Atrás tras cerrar
- **WHEN** tras cerrar la sesión pulsa «Atrás» o abre `/inicio`
- **THEN** se redirige a `/iniciar-sesion?next=<ruta>`
