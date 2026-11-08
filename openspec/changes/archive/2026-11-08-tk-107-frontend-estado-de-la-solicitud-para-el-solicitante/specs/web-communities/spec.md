## MODIFIED Requirements

### Requirement: Sin acceso hasta la aprobación
`/comunidades/<id>` MUST mostrar solo el nombre y un aviso cuando mi membresía no está aprobada: con la solicitud pendiente, «Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.»; «Solicitar acceso» sin membresía; o «No tienes acceso a esta comunidad.» si está rechazada o bloqueada. Un `platform_admin` SHALL acceder siempre, como un miembro aprobado.

#### Scenario: Pendiente
- **WHEN** abro la comunidad con la solicitud pendiente
- **THEN** veo «Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.» y ningún anuncio

#### Scenario: Administrador de plataforma pendiente
- **WHEN** un `platform_admin` con la solicitud pendiente abre la comunidad
- **THEN** ve los anuncios, «Publicar anuncio» y «Gestionar comunidad»
