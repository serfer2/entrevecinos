## Context

TK-048 introdujo `postLoginPath(token)`, que cuenta las membresías aprobadas de comunidades activas.

## Decisions

- **Mismo criterio de recuento que TK-048:** las solicitudes pendientes y las comunidades desactivadas no cuentan, así que un usuario aprobado en una y pendiente en otra va a la aprobada.
- **Varias comunidades → `/inicio`:** ya lista mis comunidades; recordar la última visitada queda fuera.

## Risks / Trade-offs

- [Quien pertenece a varias sigue pasando por `/inicio`] → necesitaría su propia historia.
