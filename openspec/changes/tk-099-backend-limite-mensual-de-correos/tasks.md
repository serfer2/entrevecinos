## 1. Dominio y BD

- [x] 1.1 `current_period` y `EmailQuotaExceeded`, con pruebas de los bordes (día 5, día 6, cambio de año, horario de verano)
- [x] 1.2 Modelo `EmailQuotaModel` y migración `0010` reversible
- [x] 1.3 Adaptador SQLAlchemy con reserva atómica y lectura del contador, con pruebas `db` (plaza 5.000, plaza 5.001, periodos distintos)

## 2. Backend

- [x] 2.1 `EmailQuota` (comprobar y reservar, avisos en los registros) y su uso en el registro y el reenvío, con pruebas
- [x] 2.2 Configuración `EMAIL_MONTHLY_LIMIT` y `EMAIL_QUOTA_RESET_DAY`, dependencias y `503` con `Retry-After`, con pruebas de endpoints
- [x] 2.3 Contrato (`registerUser`, `resendEmailVerification`, esquema `EmailQuotaExceeded`), cambios en `docs/api/README.md` y extracto del `readme.md`

## 3. Frontend

- [x] 3.1 Mensaje del `503` en el registro y el reenvío, con pruebas

## 4. Infraestructura

- [x] 4.1 Variables en el Compose de producción; filtros de métricas, alarmas y panel

## 5. Documentación

- [x] 5.1 `infra/aws/README.md` (decisión de coste, «Costes», alarmas y *runbook*), `apps/api/README.md` y `.env.example`

## 6. Verificación

- [x] 6.1 `make ci-api`, `make ci-web`, `make tf-lint` y prueba local con `EMAIL_MONTHLY_LIMIT=2`
- [ ] 6.2 `make tf-plan` y `make tf-apply`; despliegue y comprobación en producción
