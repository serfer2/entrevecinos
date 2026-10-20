# web-communities Specification

## Purpose
Pantallas de comunidades y navegación de la zona privada.
## Requirements
### Requirement: Crear una comunidad desde la interfaz
La página `/comunidades/nueva` SHALL mostrar un formulario (nombre, descripción, ciudad y código postal) que crea la comunidad y lleva a `/comunidades/<id>`, donde se muestra su nombre.

#### Scenario: Creación correcta
- **WHEN** el vecino escribe el nombre y pulsa «Crear comunidad»
- **THEN** llega a `/comunidades/<id>` con el nombre de la comunidad

### Requirement: Nombre obligatorio
El formulario MUST mostrar «El nombre de la comunidad es obligatorio.» sin llamar a la API cuando el nombre está vacío.

#### Scenario: Sin nombre
- **WHEN** se envía el formulario sin nombre
- **THEN** se ve el error bajo el campo y no hay llamada a la API

### Requirement: Navegación privada
Las páginas privadas SHALL mostrar una cabecera con «EntreVecinos», «Comunidades» (enlace a `/comunidades`) y «Mi perfil», con `aria-current="page"` en la sección actual.

#### Scenario: Sección actual
- **WHEN** el vecino está en `/perfil`
- **THEN** el enlace «Mi perfil» tiene `aria-current="page"`

### Requirement: Buscar comunidades
`/comunidades` SHALL buscar por nombre, ciudad o código postal con un formulario GET, mostrar los resultados paginados y, para cada uno, la acción según mi membresía: «Solicitar acceso» sin membresía, «Solicitud pendiente», «Entrar» si está aprobada y «Acceso no disponible» si está rechazada o bloqueada.

#### Scenario: Resultado sin membresía
- **WHEN** busco una comunidad de la que no soy miembro
- **THEN** veo el botón «Solicitar acceso»

### Requirement: Solicitar el acceso
Pulsar «Solicitar acceso» SHALL registrar la solicitud y mostrar «Solicitud pendiente», también si ya existía una membresía (sin mensaje de error), y la comunidad SHALL aparecer en «Mis comunidades» de `/inicio`.

#### Scenario: Solicitud duplicada
- **WHEN** la API responde `409`
- **THEN** se muestra el estado actual y no un error

### Requirement: Sin acceso hasta la aprobación
`/comunidades/<id>` MUST mostrar solo el nombre y un aviso cuando mi membresía no está aprobada: pendiente, «Solicitar acceso» sin membresía o «No tienes acceso a esta comunidad.» si está rechazada o bloqueada.

#### Scenario: Pendiente
- **WHEN** abro la comunidad con la solicitud pendiente
- **THEN** veo «Tu solicitud está pendiente de aprobación…» y ningún anuncio

