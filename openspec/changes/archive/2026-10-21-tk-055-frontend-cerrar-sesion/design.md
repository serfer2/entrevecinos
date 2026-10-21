## Context

La sesión es un JWT sin estado en la *cookie* `httpOnly` `ev_session`; la API no tiene endpoint de cierre de sesión.

## Decisions

- **Cerrar sesión = borrar la *cookie*:** sin revocación en la API.
- **Formulario `POST` con *Server Action***, no un enlace `GET`: evita cierres desde otra web o por *prefetch*; las *Server Actions* comprueban el origen.
- **En la cabecera, tras «Mi perfil»:** visible en todas las páginas privadas y con el mismo estilo discreto que la navegación; sin confirmación.
- **Borrar la *cookie* en la *Server Action* invalida la caché del router**, así que «Atrás» vuelve a pedir la página y el proxy redirige al inicio de sesión.

## Risks / Trade-offs

- [Un token copiado antes del cierre sigue siendo válido hasta caducar] → revocación o tokens cortos, si hiciera falta.
