## Context

El reenvío del correo de validación (TK-059, TK-099) ya resuelve los mismos problemas: respuesta que no revela cuentas, cupo comprobado antes de buscar la cuenta, un enlace por minuto y envío en segundo plano tras confirmar la transacción. La tabla `password_reset` (TK-100) borra los enlaces usados o sustituidos.

## Goals / Non-Goals

**Goals:** pedir el enlace sin revelar cuentas ni permitir abusos, consumiendo el cupo.

**Non-Goals:** cambiar la contraseña con el enlace (TK-102); interfaz (TK-103); límites por IP del proxy (TK-105).

## Decisions

- **`202` con cuerpo `{"detail": …}`, como el reenvío:** el ticket proponía `202` sin cuerpo; se mantiene la forma de `resendEmailVerification` para que la web trate igual los dos formularios. El mensaje es fijo: «Si hay una cuenta con ese correo, te enviaremos un enlace para restablecer la contraseña.».
- **Orden de `RequestPasswordReset`:** cupo → cuenta → límite de un minuto → reservar plaza → emitir. Igual que el reenvío: el `503` no depende de que la cuenta exista y solo se consume cupo cuando se envía.
- **Qué cuentas reciben el enlace:** `deleted_at` nulo y (`is_active` o `email_verification_pending`). Así reciben el enlace las activas (incluido un `platform_admin` sin validar) y las pendientes de validar; no lo reciben las desactivadas con el correo validado (bloqueadas por otros motivos). Regla en la entidad: `User.can_reset_password`.
- **`PasswordResetIssuer` separado de `EmailVerificationIssuer`:** comparten `hash_token`, pero el enlace, la caducidad (minutos, no horas) y el texto son distintos. `replace` borra los enlaces anteriores en lugar de marcarlos.
- **Caducidad en minutos (`PASSWORD_RESET_TTL_MINUTES`, 60):** una hora es corta para un enlace que da acceso a la cuenta; en minutos se puede ajustar sin cambiar de unidad.
- **Registros:** el caso de uso no registra el correo pedido ni el *token*; el envío fallido ya se registra solo con el asunto (`send_in_background`).

## Risks / Trade-offs

- [Alguien pide enlaces para correos ajenos] → un enlace por minuto y cuenta, límite por IP del proxy (TK-105) y cupo mensual con aviso al 80 %.
- [Un abuso sostenido agota el cupo y bloquea también los registros hasta el día 6] → aceptado con tráfico bajo; la alarma `email-quota-80` avisa antes.
- [Buscar una cuenta existente tarda algo más] → diferencia de milisegundos, tapada por la latencia de red; sin espera artificial.
