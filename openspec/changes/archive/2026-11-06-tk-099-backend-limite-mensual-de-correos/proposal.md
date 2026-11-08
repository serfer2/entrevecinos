## Why

HU-40 AC5: el correo de producción no puede costar más que el plan más barato de Brevo (5.000 correos al mes) y el proyecto debe seguir por debajo de 40 €/mes. Es una **restricción de costes**. Hoy nada limita los envíos: un fallo o un abuso agotaría el plan o haría que Brevo suspendiera la cuenta. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-40-recibir-el-correo-de-validacion-en-cualquier-direccion/TK-099-backend-limite-mensual-de-correos.md`.

## What Changes

- **Cupo de 5.000 correos por periodo**, del día 6 a las 00:00 (`Europe/Madrid`) al día 6 del mes siguiente. Contador en PostgreSQL (`email_quota`, migración `0010`) con reserva atómica.
- **Registro:** reserva plaza antes de crear la cuenta. **Reenvío:** comprueba el cupo en toda petición, para no revelar si la cuenta existe, y reserva solo cuando envía. Sin cupo, `503` con `code: email_quota_exceeded` y `Retry-After`, sin crear nada.
- **Registros de la API:** aviso al llegar al 80 % y error en cada bloqueo, sin direcciones de correo.
- **Configuración:** `EMAIL_MONTHLY_LIMIT` (5000) y `EMAIL_QUOTA_RESET_DAY` (6), explícitas en el Compose de producción.
- **Contrato:** `503` en `registerUser` y `resendEmailVerification`, y extracto del `readme.md` regenerado.
- **Web:** mensaje en el registro y en el reenvío.
- **Alarmas:** `email-quota-80` y `email-quota-exceeded`.
- **Documentación:** el límite figura como restricción de costes en la guía («Decisiones de arquitectura» y «Costes»), en `apps/api/README.md` y en `.env.example`.

## Capabilities

### New Capabilities
- `email-quota`: límite de correos por periodo mensual, por coste.

### Modified Capabilities
- (ninguna; las specs de registro y reenvío no cambian salvo por el `503`, que recoge `email-quota`)

## Impact

- API: `domain/mail`, `application/mail`, casos de uso de registro y reenvío, adaptador SQLAlchemy, modelo y migración `0010`, errores y dependencias; pruebas.
- Contrato: `docs/api/` (dos operaciones y un esquema nuevo); `readme.md` §4 regenerado.
- Web: `features/auth/actions.ts` y sus pruebas.
- Infraestructura: `infra/docker-compose.prod.yml` y `infra/aws/modules/observability/`; `infra/aws/README.md` («Decisiones de arquitectura», «Costes», «Observabilidad y alertas»). Exige `make tf-apply` antes del despliegue.
