## Context

La validación del correo (TK-057, TK-063) guarda sus enlaces con hash y marca los usados y sustituidos (`used_at`, `superseded_at`) para que la web explique por qué un enlace no vale. Los JWT duran 24 horas y no se pueden revocar uno a uno.

## Goals / Non-Goals

**Goals:** guardar enlaces de restablecimiento sin el *token* en claro y registrar la fecha del último cambio de contraseña.

**Non-Goals:** lógica de solicitud y cambio (TK-101, TK-102); limpieza periódica de enlaces caducados.

## Decisions

- **Mismo esquema de *token* que la validación:** solo el SHA-256 (`CHAR(64)`, PK). Una copia de la base no permite usar un enlace.
- **Sin `used_at` ni `superseded_at`:** un enlace usado o sustituido se borra. A quien abre un enlace que no vale le basta con pedir otro; no hace falta distinguir el motivo, y así la tabla no acumula filas.
- **Sin índice único parcial:** como pedir un enlace borra los anteriores del usuario en la misma transacción, como mucho hay uno por usuario; el índice por `user_id` basta para borrarlos y para consultar el más reciente (límite de uno por minuto).
- **`users.password_changed_at` nulo por defecto, sin *backfill*:** las cuentas existentes no han cambiado la contraseña desde que existe la columna y sus sesiones deben seguir valiendo. TK-102 rechazará los JWT con `iat` anterior a esta fecha.

## Risks / Trade-offs

- [Enlaces caducados que nadie vuelve a pedir quedan en la tabla] → se borran al pedir otro o al borrar el usuario; volumen despreciable con el cupo de 5.000 correos por periodo.
