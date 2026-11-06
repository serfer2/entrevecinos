# TK-099 · Backend: límite de 5.000 correos por periodo mensual

| Campo | Valor |
|---|---|
| **Tipo** | Backend (con BD, contrato, web y alarma) |
| **Componente** | `apps/api` (dominio, aplicación, infraestructura, presentación y migración `0010`), `docs/api/openapi.yaml`, `apps/web` (mensajes del registro y del reenvío), `infra/aws/modules/observability/`, `infra/docker-compose.prod.yml` |
| **Historia** | HU-40 Recibir el correo de validación en cualquier dirección (Épica 13) |
| **Prioridad** | Alta (restricción de costes) |
| **Depende de** | TK-098 |
| **Referencias** | `apps/api/src/entrevecinos/application/users/ports.py` (`EmailSender`); `presentation/v1/auth.py` (`register`, `resend_email_verification`, `send_in_background`); TK-096 (plan gratuito de Brevo: 300 al día; el de pago más barato, 5.000 al mes) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

**El límite es una restricción de costes.** El correo de producción no puede generar más gasto que el plan de pago más barato de Brevo (5.000 correos al mes, ≈ 9 USD/mes, TK-096), y el gasto total del proyecto debe seguir por debajo del límite de 40 €/mes (TK-078). Un tope en la propia aplicación garantiza ese máximo aunque falle otra protección. Subirlo es una decisión de coste: se revisa junto con el presupuesto.

La API envía correo en el registro (`POST /auth/register`) y en el reenvío del enlace de validación (`POST /auth/email-verification/resend`). No hay ningún tope: un fallo de la aplicación o un abuso (registros masivos o reenvíos automatizados) agotaría el plan de Brevo, generaría coste o haría que Brevo suspendiera la cuenta. Los límites por IP del proxy solo frenan a un único origen.

**Objetivo:** no enviar más de **5.000 correos por periodo**, por coste. El periodo va **del día 6 de un mes, a las 00:00, al día 6 del mes siguiente, a las 00:00**. Alcanzado el límite, la API bloquea todo envío hasta el siguiente periodo y avisa.

## 2. Alcance

**Incluye**
- **Periodo:**
  - empieza el día 6 más reciente a las 00:00 en hora de `Europe/Madrid` (asumido; mismo calendario que ve el equipo), es decir `[6 del mes M 00:00, 6 del mes M+1 00:00)`;
  - del 1 al 5 de un mes, cuenta el periodo que empezó el 6 del mes anterior;
  - el cálculo es una función pura del dominio, con pruebas de los bordes: día 5 a las 23:59, día 6 a las 00:00 y cambio de año (diciembre → enero).
- **Cupo persistente** en PostgreSQL (migración `0010`, con `downgrade()`):
  - tabla `email_quota` (`period_start DATE` PK, `sent INTEGER NOT NULL DEFAULT 0 CHECK (sent >= 0)`, `updated_at`);
  - **reserva atómica de una plaza antes de enviar**: `INSERT … ON CONFLICT (period_start) DO UPDATE SET sent = email_quota.sent + 1 WHERE email_quota.sent < :limit RETURNING sent`;
  - si no devuelve fila, el límite está alcanzado. Sin condiciones de carrera entre peticiones concurrentes;
  - una plaza reservada cuenta aunque el envío falle después (criterio conservador);
  - el periodo nuevo empieza en cero solo, sin tareas programadas.
- **Aplicación:**
  - puerto `EmailQuota` (`reserve() -> bool`) con su adaptador SQLAlchemy;
  - `RegisterUser` y `ResendEmailVerification` reservan la plaza **antes** de crear la cuenta o el enlace;
  - sin plaza, error de dominio `EmailQuotaExceeded`: no se crea la cuenta, no se genera enlace y no se envía nada.
- **API:**
  - `EmailQuotaExceeded` → `503 Service Unavailable` con `{"detail": "...", "code": "email_quota_exceeded"}` y `Retry-After` con los segundos hasta el inicio del siguiente periodo;
  - el reenvío sigue sin revelar si la cuenta existe: el `503` depende del cupo global, no de la cuenta;
  - configuración `EMAIL_MONTHLY_LIMIT` (por defecto `5000`) y `EMAIL_QUOTA_RESET_DAY` (por defecto `6`), validadas en `Settings` (límite > 0; día entre 1 y 28), y documentadas en `.env.example` y `apps/api/README.md`.
- **Registros:**
  - un aviso al cruzar el 80 % del cupo («Cupo de correo al 80 %: 4000 de 5000»), una vez por periodo;
  - un error en cada intento bloqueado («Límite mensual de correos alcanzado»), sin la dirección de correo.
- **Contrato:** `503` con su esquema en `registerUser` y `resendEmailVerification` de `docs/api/openapi.yaml`, y regenerar el extracto del `readme.md` (TK-077).
- **Web:** en el registro y en el reenvío, el `503` con `email_quota_exceeded` muestra «Ahora mismo no podemos enviar correos de validación. Inténtalo de nuevo en unos días.», sin perder los datos del formulario.
- **Alarmas** (`modules/observability`), con aviso al volver a `OK`:
  - filtros de métricas sobre `/entrevecinos/prod/app/api` → `EmailQuotaWarning` y `EmailQuotaExceeded` en `Entrevecinos/Logs`;
  - alarmas `entrevecinos-prod-email-quota-80` y `entrevecinos-prod-email-quota-exceeded`;
  - entrada en el *runbook*: qué hacer al llegar al límite (revisar abusos en los registros del proxy y de la API, subir el límite o el plan de Brevo).
- **Producción:** `EMAIL_MONTHLY_LIMIT=5000` y `EMAIL_QUOTA_RESET_DAY=6` explícitos en `infra/docker-compose.prod.yml`, con un comentario que remite a la decisión de coste.
- **Documentación del motivo (restricción de costes):**
  - `infra/aws/README.md`, «Decisiones de arquitectura»: entrada «Límite de 5.000 correos por periodo, por coste (TK-099)», con qué es, por qué (coste máximo del correo igual al plan más barato de Brevo y gasto total dentro de los 40 €/mes), su impacto (bloqueo del registro al alcanzarlo), las mitigaciones (alarmas y límites del proxy), cuándo revisarlo (crecimiento real de registros) y cómo subirlo (variable, presupuesto y plan de Brevo);
  - `infra/aws/README.md`, «Costes»: el correo con su límite y el gasto máximo que permite;
  - `apps/api/README.md` y `.env.example`: las dos variables, indicando que el valor de producción responde a una restricción de costes.

**No incluye**
- Cupos por usuario o por IP (los límites del proxy ya existen).
- Encolar y enviar más tarde los correos bloqueados: el usuario lo reintenta en el siguiente periodo.
- Sincronizar el contador con el de Brevo: el cupo propio es el que manda; Brevo sigue con sus 300 al día.

## 3. Requisitos técnicos

- Arquitectura limpia: el cálculo del periodo y el error, en `domain`; el puerto, en `application`; el SQL, en `infrastructure` (`tests/test_architecture.py`).
- La reserva y la creación de la cuenta van en la misma transacción. Si el registro falla después (por ejemplo, un `409` de correo duplicado), la plaza no se consume.
- Las direcciones de correo no aparecen en los registros.
- Pruebas:
  - periodo: bordes, cambio de año y zona horaria;
  - reserva: la plaza 5.000 se concede y la 5.001 se rechaza, contra PostgreSQL (marcador `db`);
  - endpoints: `503` con `Retry-After` y sin cuenta creada;
  - web: el mensaje y el formulario conservado;
  - migración reversible.

## 4. Criterios de aceptación

**AC1 — Límite respetado**
- **Given** 4.999 correos enviados en el periodo actual
- **When** se registra un vecino nuevo
- **Then** se envía su correo (el 5.000) y el contador queda en 5.000

**AC2 — Bloqueo al alcanzar el límite**
- **Given** 5.000 correos enviados en el periodo actual
- **When** alguien se registra o pide el reenvío del enlace
- **Then** la API responde `503` con `email_quota_exceeded` y `Retry-After`, no crea la cuenta ni envía nada, y la web muestra el mensaje

**AC3 — Periodo del 6 al 6**
- **Given** el límite alcanzado el 20 de marzo
- **When** llega el 6 de abril a las 00:00 (hora de Madrid)
- **Then** los envíos vuelven a funcionar con el contador del periodo nuevo en cero; y del 1 al 5 de abril siguen bloqueados

**AC4 — Avisos**
- **Given** las alarmas de cupo
- **When** se cruza el 80 % o se bloquea un envío
- **Then** recibo el aviso correspondiente por correo

**AC5 — Motivo documentado**
- **Given** `infra/aws/README.md`
- **When** consulto «Decisiones de arquitectura» y «Costes»
- **Then** encuentro que el límite de 5.000 correos por periodo es una restricción de costes, el gasto máximo que fija y cómo se revisa

**AC6 — Sin condiciones de carrera**
- **Given** 4.999 correos enviados
- **When** llegan dos registros a la vez
- **Then** solo uno obtiene plaza y el otro recibe `503`

## 5. Plan de tareas

1. Dominio: periodo y error, con pruebas.
2. BD: migración `0010` y adaptador de reserva atómica, con pruebas `db`.
3. Aplicación y API: reserva en el registro y el reenvío, `503`, configuración y registros, con pruebas.
4. Contrato y extracto del `readme.md`.
5. Web: mensaje del `503`, con pruebas.
6. Infraestructura: variables de producción, filtros, alarmas y *runbook*; decisión de coste y «Costes» en `infra/aws/README.md`.
7. Verificación: `make ci-api`, `make ci-web`, `make tf-lint`; prueba en local con `EMAIL_MONTHLY_LIMIT=2`.

## 6. Verificación

```bash
# Local, con un límite bajo
EMAIL_MONTHLY_LIMIT=2 make dev
curl -s -X POST localhost:8000/v1/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"a3@example.com","password":"…","full_name":"Prueba"}' -i | head -5   # tercera: 503 y Retry-After
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -d entrevecinos -c 'SELECT * FROM email_quota'
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Contrato, `.env.example`, `apps/api/README.md` e `infra/aws/README.md` actualizados, con el límite documentado como restricción de costes.
- [x] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Denegación de servicio por agotamiento:** un atacante que fuerce 5.000 registros bloquea el registro de todos hasta el día 6. Los límites por IP del proxy lo dificultan, y las alarmas del 80 % y del 100 % permiten reaccionar (bloquear el origen o subir el límite).
- **Zona horaria:** se asume `Europe/Madrid`; UTC cambiaría el corte una o dos horas.
- **Plaza consumida en fallos de envío:** conservador; con la alarma de fallos de envío (TK-097) se detecta si muchas plazas se pierden.
- **Coherencia con Brevo:** 5.000 al mes encaja con su plan de pago más barato; en el gratuito, el límite diario de 300 de Brevo puede llegar antes.
