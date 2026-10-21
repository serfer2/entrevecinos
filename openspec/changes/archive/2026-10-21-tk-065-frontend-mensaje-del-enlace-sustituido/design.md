## Context

TK-064 añade el motivo en el `code` del `400`.

## Decisions

- **Solo `email_already_verified` mantiene el comportamiento anterior** (sesión → `/comunidades`; sin ella → inicio de sesión con aviso). Un `code` desconocido se trata como `invalido`: nunca se afirma que el correo está validado sin saberlo.
- **`reemplazado` reutiliza el reenvío de `caducado`:** en ambos casos la cuenta sigue pendiente.

## Risks / Trade-offs

- [El correo viaja en la URL] → igual que en `caducado`.
