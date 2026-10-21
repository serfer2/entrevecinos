## ADDED Requirements

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
