## MODIFIED Requirements

### Requirement: Crear una comunidad desde la interfaz
La página `/comunidades/nueva` SHALL mostrar un formulario (nombre, descripción, ciudad y código postal) que avisa de la revisión por un administrador y crea la comunidad. Si queda pendiente, SHALL llevar a `/inicio` con «Hemos recibido tu comunidad. Un administrador la revisará antes de activarla.»; si queda activa, a `/comunidades/<id>`, donde se muestra su nombre.

#### Scenario: Creación pendiente
- **WHEN** un vecino escribe el nombre y pulsa «Crear comunidad»
- **THEN** llega a `/inicio` con el aviso y ve la comunidad en «Mis comunidades» como «Pendiente de aprobación», sin enlace

#### Scenario: Creación activa
- **WHEN** la API devuelve la comunidad con `is_active: true`
- **THEN** llega a `/comunidades/<id>` con el nombre de la comunidad
