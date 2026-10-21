## Context

Con TK-063 la API conserva los enlaces usados y sustituidos.

## Decisions

- **Manda el estado de la cuenta:** con el correo validado, cualquier enlace suyo responde `email_already_verified`, también uno sustituido.
- **La sustitución va antes que la caducidad:** el usuario debe abrir el último correo, no pedir otro.
- **`email` en `verification_superseded`:** igual que en el `410`; solo lo recibe quien tiene un token emitido de verdad. Un token desconocido no revela nada.
- **Mismo estado `400`:** compatible con clientes que solo miran el estado.

## Risks / Trade-offs

- [Un enlace usado de una cuenta validada no distingue «ya usado» de «sustituido»] → aceptado: para el usuario es lo mismo.
