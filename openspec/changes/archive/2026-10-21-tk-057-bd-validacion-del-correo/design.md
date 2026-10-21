## Context

Hasta ahora todas las cuentas se activaban al registrarse.

## Decisions

- **`CHECK (NOT is_active OR email_verified_at IS NOT NULL OR platform_role = 'platform_admin')`:** la base de datos garantiza la regla de HU-25.
- **Backfill `email_verified_at = created_at`:** las cuentas existentes no quedan fuera.
- **Solo el SHA-256 del token (`token_hash CHAR(64)`, PK):** el token en claro solo viaja en el correo. Un token usado se borra; sin `used_at`.
- **`is_active` mantiene `DEFAULT true`;** el registro inserta `false` explícitamente.

## Risks / Trade-offs

- [Nombrar un `platform_admin` a mano sigue funcionando aunque no haya validado su correo] → aceptado.
