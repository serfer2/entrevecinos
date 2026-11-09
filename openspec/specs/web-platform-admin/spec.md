# web-platform-admin Specification

## Purpose
Pantallas del administrador de plataforma (`/admin/comunidades`): aprobación y rechazo de comunidades.
## Requirements
### Requirement: Aprobar comunidades desde la interfaz
La página `/admin/comunidades` SHALL mostrar a un `platform_admin` las comunidades pendientes (la más antigua primero, con nombre, ubicación, fecha y descripción) y un botón «Aprobar» que la activa y muestra «Comunidad aprobada.»; sin pendientes muestra «No hay comunidades pendientes de aprobación.». `/inicio` SHALL enlazarla solo para el `platform_admin`.

#### Scenario: Aprobación
- **WHEN** un `platform_admin` pulsa «Aprobar» en una comunidad pendiente
- **THEN** ve «Comunidad aprobada.», la comunidad desaparece de la lista y su creador puede abrirla desde «Mis comunidades»

#### Scenario: Vecino
- **WHEN** un usuario sin rol `platform_admin` abre `/admin/comunidades`
- **THEN** ve la página de no encontrado y `/inicio` no le muestra el enlace

### Requirement: Rechazar comunidades desde la interfaz
Cada comunidad de `/admin/comunidades` SHALL ofrecer, junto a «Aprobar», un botón «Rechazar» que pide confirmación («¿Rechazar la comunidad <nombre>?») antes de llamar a `DELETE /admin/communities/{id}`. Tras el rechazo, la página MUST mostrar «Se ha rechazado la comunidad <nombre>.» y la comunidad desaparece de la lista. Si la API responde `409`, MUST mostrar «Esta comunidad ya está activa: no se puede rechazar.»; si responde `404`, «Esta comunidad ya no está pendiente.»; ante otro error, «No se pudo rechazar la comunidad. Inténtalo de nuevo.». Cada comunidad SHALL tener el ancla `comunidad-<id>`.

#### Scenario: Rechazo
- **WHEN** un `platform_admin` pulsa «Rechazar» en una comunidad pendiente y confirma
- **THEN** ve «Se ha rechazado la comunidad <nombre>.» y la comunidad desaparece de la lista

#### Scenario: Ya aprobada
- **WHEN** rechaza una comunidad que otro administrador acaba de aprobar
- **THEN** ve «Esta comunidad ya está activa: no se puede rechazar.»

#### Scenario: Enlace del correo
- **WHEN** abre `/admin/comunidades#comunidad-<id>`
- **THEN** la página se desplaza a esa comunidad
