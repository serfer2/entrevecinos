## Context

`ChangeMembershipStatus.execute` revisa solicitudes y bloquea o desbloquea miembros, y devuelve el `MembershipDetail` nuevo; solo lo usa el endpoint `update_membership`. `MembershipNotices` (TK-106) prepara avisos y reserva cupo.

## Goals / Non-Goals

**Goals:** avisar al solicitante cuando se aprueba su solicitud, sin condicionar la aprobación.

**Non-Goals:** avisos de rechazo, bloqueo o expulsión; texto de la web (TK-107).

## Decisions

- **`ChangeMembershipStatus` devuelve `MembershipChange(detail, previous)`** con la propiedad `approves_request` (`pending → approved`). La regla de cuándo avisar vive en la aplicación; el desbloqueo (`blocked → approved`) no cuenta.
- **`MembershipNotices.request_approved(community_id, user_id)`** busca la comunidad (activa) y la cuenta (activa y no borrada), reserva una plaza y prepara el mensaje; devuelve `None` si no procede o no hay cupo. Por eso `MembershipNotices` recibe también los repositorios de comunidades y usuarios.
- **Mensaje sin datos de quien aprueba** (asumido): basta con la comunidad y el enlace.

## Risks / Trade-offs

- [Un administrador que aprueba y rechaza en bucle] → no es posible: una solicitud solo se revisa una vez (`409` si ya está revisada); el desbloqueo no avisa.
