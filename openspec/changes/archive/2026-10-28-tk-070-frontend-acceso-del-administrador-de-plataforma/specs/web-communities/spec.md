## MODIFIED Requirements

### Requirement: Buscar comunidades
`/comunidades` SHALL buscar por nombre, ciudad o código postal con un formulario GET, mostrar los resultados paginados y, para cada uno, la acción según mi membresía: «Solicitar acceso» sin membresía, «Solicitud pendiente», «Entrar» si está aprobada y «Acceso no disponible» si está rechazada o bloqueada. A un `platform_admin` SHALL mostrarle siempre «Entrar».

#### Scenario: Resultado sin membresía
- **WHEN** busco una comunidad de la que no soy miembro
- **THEN** veo el botón «Solicitar acceso»

#### Scenario: Administrador de plataforma
- **WHEN** un `platform_admin` busca comunidades
- **THEN** ve «Entrar» en todas, sea cual sea su membresía

### Requirement: Sin acceso hasta la aprobación
`/comunidades/<id>` MUST mostrar solo el nombre y un aviso cuando mi membresía no está aprobada: pendiente, «Solicitar acceso» sin membresía o «No tienes acceso a esta comunidad.» si está rechazada o bloqueada. Un `platform_admin` SHALL acceder siempre, como un miembro aprobado.

#### Scenario: Pendiente
- **WHEN** abro la comunidad con la solicitud pendiente
- **THEN** veo «Tu solicitud está pendiente de aprobación…» y ningún anuncio

#### Scenario: Administrador de plataforma pendiente
- **WHEN** un `platform_admin` con la solicitud pendiente abre la comunidad
- **THEN** ve los anuncios, «Publicar anuncio» y «Gestionar comunidad»
