## Context

TK-017 dejó la revisión de solicitudes (`ReviewMembership`) y `CommunityAccess`; TK-028/TK-036 el filtro de visibilidad del listado y `ListingVisibility`.

## Goals / Non-Goals

**Goals:** bloquear, desbloquear y expulsar con protecciones; efecto inmediato en el acceso y en la visibilidad de los anuncios.

**Non-Goals:** cambio de rol; interfaz para salir de una comunidad.

## Decisions

- **`ChangeMembershipStatus`** (sustituye a `ReviewMembership`): `pending → approved | rejected`, `approved → blocked`, `blocked → approved`. Revisar dos veces una solicitud sigue respondiendo «La solicitud ya se ha revisado.»; otras transiciones, bloquear a un administrador o a uno mismo → `MembershipChangeRejected` (409 con su mensaje). Al desbloquear se conserva `joined_at`.
- **`RemoveMembership`**: la propia siempre (salida); la de otros, solo `community_admin` o `platform_admin`; un administrador no expulsa a otro (403, salvo `platform_admin`); nunca el último administrador aprobado (409).
- **Anuncios ocultos al consultar**, sin tocar `listing.status` (no se mezcla con `hidden` de la moderación y desbloquear no necesita restaurar nada): `OWNER_IS_MEMBER` (`EXISTS` por la PK de `community_membership`) en el filtro común del listado y como columna en `listing_with_owner()`, que rellena `Listing.owner_is_member`; `ListingVisibility` trata ese anuncio como retirado (solo autor y gestores; 404 para el resto). La expulsión también los oculta (asumido).

## Risks / Trade-offs

- [Un `EXISTS` más por anuncio listado] → usa la PK; despreciable con el volumen del MVP.
