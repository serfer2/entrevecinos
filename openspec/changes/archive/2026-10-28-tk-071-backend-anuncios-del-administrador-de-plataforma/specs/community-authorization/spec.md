## MODIFIED Requirements

### Requirement: Anuncios de miembros bloqueados o expulsados
Los anuncios de un autor sin membresía aprobada MUST dejar de aparecer en el listado, la búsqueda y su `total`, y su detalle SHALL responder `404` a los miembros (lo ven el autor y los gestores); al desbloquearlo vuelven a mostrarse con su estado original. Un autor `platform_admin` SHALL contar como miembro aprobado de cualquier comunidad (como en `require_member`): sus anuncios se muestran aunque no tenga membresía o la suya no esté aprobada.

#### Scenario: Bloqueo
- **WHEN** se bloquea a un miembro con anuncios
- **THEN** los demás miembros dejan de verlos y vuelven a verlos al desbloquearlo

#### Scenario: Anuncios de un platform_admin
- **WHEN** un `platform_admin` con la solicitud pendiente publica un anuncio en una comunidad
- **THEN** los miembros lo ven en el listado y en su detalle
