# web-platform-admin Specification

## Purpose
Pantallas del administrador de plataforma (`/admin/comunidades`): aprobación de comunidades.
## Requirements
### Requirement: Aprobar comunidades desde la interfaz
La página `/admin/comunidades` SHALL mostrar a un `platform_admin` las comunidades pendientes (la más antigua primero, con nombre, ubicación, fecha y descripción) y un botón «Aprobar» que la activa y muestra «Comunidad aprobada.»; sin pendientes muestra «No hay comunidades pendientes de aprobación.». `/inicio` SHALL enlazarla solo para el `platform_admin`.

#### Scenario: Aprobación
- **WHEN** un `platform_admin` pulsa «Aprobar» en una comunidad pendiente
- **THEN** ve «Comunidad aprobada.», la comunidad desaparece de la lista y su creador puede abrirla desde «Mis comunidades»

#### Scenario: Vecino
- **WHEN** un usuario sin rol `platform_admin` abre `/admin/comunidades`
- **THEN** ve la página de no encontrado y `/inicio` no le muestra el enlace

