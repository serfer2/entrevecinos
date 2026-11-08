## Context

La API emite JWT de 24 horas (`iat`, `exp`, `sub`) sin estado en el servidor. `GetCurrentUser` ya carga el usuario en cada petición autenticada. `AuthenticateUser` reescribe el hash con `update_password_hash` cuando cambian los parámetros de Argon2, lo que no es un cambio de contraseña. La tabla `password_reset` y `users.password_changed_at` existen desde TK-100.

## Goals / Non-Goals

**Goals:** cambiar la contraseña con el enlace, invalidar el enlace y las sesiones anteriores, y avisar del cambio.

**Non-Goals:** la interfaz (TK-104); cambiar la contraseña desde el perfil.

## Decisions

- **`204` sin iniciar sesión:** la web lleva al inicio de sesión; así, quien abre el enlace demuestra también que recuerda la contraseña nueva, y el endpoint no emite ningún JWT.
- **`UserRepository.change_password` separado de `update_password_hash`:** solo el cambio real fija `password_changed_at`; la reescritura del hash al iniciar sesión no debe cerrar sesiones.
- **`password_changed_at = statement_timestamp()` de PostgreSQL:** el momento de la sentencia que cambia la contraseña, como `users.updated_at`. `now()` devolvería el inicio de la transacción y aceptaría *tokens* emitidos entre ese inicio y el cambio.
- **`TokenService.decode` devuelve `TokenClaims(user_id, issued_at)`** y `GetCurrentUser.execute(claims)` compara: `issued_at < password_changed_at` truncado al segundo → `NotAuthenticated`. `iat` va en segundos enteros; truncar evita rechazar un *token* emitido en el mismo segundo del cambio. No añade consultas: el usuario ya se carga.
- **Errores propios (`PasswordResetInvalid`, `PasswordResetExpired`)** con códigos `password_reset_invalid` (`400`) y `password_reset_expired` (`410`), sin el correo en la respuesta: la web solo ofrece pedir otro enlace.
- **Comprobación de la cuenta al confirmar:** la misma regla que al pedirlo (`User.can_reset_password`); una cuenta borrada o bloqueada entre medias recibe `400`.
- **Cuenta sin validar:** `mark_email_verified` tras cambiar la contraseña; el enlace demuestra que el correo es suyo.
- **Aviso sin cupo:** `EmailQuota.reserve()` lanza `EmailQuotaExceeded`, ya registrado como error; el caso de uso lo captura y no envía el aviso. El cambio que pide el usuario prima sobre el aviso.

## Risks / Trade-offs

- [Un JWT robado sigue valiendo hasta que se cambie la contraseña o caduque] → es el límite de los JWT sin estado; cambiar la contraseña ya lo corta.
- [Sin cupo no llega el aviso] → caso raro (cupo agotado); queda en el registro de la API y la alarma `email-quota-exceeded` avisa al equipo.
