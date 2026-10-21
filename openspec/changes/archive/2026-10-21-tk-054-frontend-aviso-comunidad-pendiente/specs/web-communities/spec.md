## ADDED Requirements

### Requirement: Aviso de comunidad pendiente
Si el usuario ya tiene una comunidad pendiente de aprobación, `/comunidades/nueva` SHALL mostrar «Ya tienes una comunidad pendiente de aprobación: «{nombre}». Podrás crear otra cuando un administrador la revise.» en lugar del formulario; si la API responde `409` al crear, el formulario SHALL mostrar «Ya tienes una comunidad pendiente de aprobación.» conservando los valores.

#### Scenario: Con una comunidad pendiente
- **WHEN** un vecino con una comunidad pendiente abre `/comunidades/nueva`
- **THEN** ve el aviso con su nombre y no ve el formulario

#### Scenario: Tras la aprobación
- **WHEN** su comunidad se aprueba y vuelve a `/comunidades/nueva`
- **THEN** ve el formulario
