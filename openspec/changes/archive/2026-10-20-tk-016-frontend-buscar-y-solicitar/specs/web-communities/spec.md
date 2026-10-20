## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Navegación privada
Las páginas privadas SHALL mostrar una cabecera con «EntreVecinos», «Comunidades» (enlace a `/comunidades`) y «Mi perfil», con `aria-current="page"` en la sección actual.

#### Scenario: Sección actual
- **WHEN** el vecino está en `/perfil`
- **THEN** el enlace «Mi perfil» tiene `aria-current="page"`
