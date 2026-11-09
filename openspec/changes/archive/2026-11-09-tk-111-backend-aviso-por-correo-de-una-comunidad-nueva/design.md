## Context

`MembershipNotices` (TK-106/TK-108) prepara avisos reservando una plaza del cupo por mensaje; los endpoints los envían con `BackgroundTasks` y `send_in_background` tras confirmar la transacción. `create_community` no envía nada.

## Goals / Non-Goals

**Goals:** avisar a los `platform_admin` de cada comunidad pendiente sin condicionar la creación.

**Non-Goals:** enlaces que aprueben o rechacen sin sesión; aviso al creador.

## Decisions

- **Clase nueva `CommunityNotices`**, en lugar de ampliar `MembershipNotices`: el aviso no trata de membresías y solo necesita `UserRepository`, `EmailQuota` y la URL pública. Mismo patrón: plaza por mensaje y corte al agotarse el cupo.
- **`UserRepository.list_platform_admins()`**: activos, no borrados, por nombre. Va en el repositorio de usuarios porque el rol de plataforma es del usuario.
- **Fechas** con `QUOTA_TIMEZONE` (Europe/Madrid) y el formato `%d/%m/%Y`, como el aviso de cambio de contraseña.
- **Datos de contacto del creador incluidos**: los destinatarios son la administración de la plataforma (ticket §8); los avisos a vecinos de TK-106 siguen sin ellos.
- **Ancla en el enlace** (`#comunidad-{id}`), que TK-113 ya añadió a `/admin/comunidades`.

## Risks / Trade-offs

- [Datos personales en buzones de terceros] → solo los administradores de plataforma, que ya ven esos datos al revisar la comunidad.
