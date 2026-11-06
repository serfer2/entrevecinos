# TK-097 · Infraestructura: correo de producción sin *sandbox* y aviso de fallos de envío

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / observabilidad |
| **Componente** | `infra/aws/envs/prod/` (`ses_test_recipients`), `infra/aws/modules/mail/`, `infra/aws/modules/compute/` (permisos de envío), `infra/aws/modules/observability/`, `infra/aws/README.md` |
| **Historia** | HU-40 Recibir el correo de validación en cualquier dirección (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-098, TK-091 |
| **Referencias** | TK-083 (identidades de prueba mientras dure el *sandbox*); TK-091 (alarmas y filtros de métricas); `apps/api/src/entrevecinos/presentation/v1/auth.py` (`send_in_background`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Mientras duraba el *sandbox*, TK-083 verificó destinatarios de prueba (`ses_test_recipients`) y el rol de la instancia puede enviar a ellos. Con el correo de producción por Brevo (TK-096 y TK-098) sobran; SES se conserva solo como vuelta atrás.

Además, un fallo de envío hoy pasa desapercibido. La API envía el correo después de responder (`send_in_background`), así que el registro termina bien y solo queda la línea «No se pudo enviar el correo» en `/entrevecinos/prod/app/api`. Por eso nadie notó que el *sandbox* bloqueaba los registros. La alarma `api-errors` no salta con un solo fallo: su umbral es de más de 10 errores en 5 minutos.

**Objetivo:** enviar a cualquier dirección sin restos del *sandbox*, comprobarlo de extremo a extremo y avisar del primer correo que no salga.

## 2. Alcance

**Incluye**
- **Sin restos del *sandbox*:**
  - `ses_test_recipients = []` en `prod.tfvars` y en el ejemplo, de modo que Terraform borre las identidades de prueba;
  - el permiso `ses:SendEmail` del rol de la instancia queda limitado a la identidad del dominio y al *configuration set*.
- **Alarma `entrevecinos-prod-email-send-failures`** (`modules/observability`):
  - filtro de métricas sobre `/entrevecinos/prod/app/api` con el mensaje «No se pudo enviar el correo»;
  - métrica `EmailSendFailures` en `Entrevecinos/Logs`;
  - salta con más de 0 fallos en 5 minutos, con aviso al volver a `OK` y los datos ausentes como correctos;
  - nueva fila en el panel y en el *runbook* de alarmas.
- **Comprobaciones:**
  - un registro con una dirección inexistente de un proveedor conocido (asumido: una de Gmail generada al azar): Brevo lo registra como rebote en sus registros transaccionales y no cuenta como fallo de envío;
  - registro de extremo a extremo en `https://entrevecinos.org` con al menos dos direcciones reales no verificadas de proveedores distintos (asumido: Gmail y Outlook): el correo llega a la bandeja de entrada y sus cabeceras muestran `spf=pass`, `dkim=pass` y `dmarc=pass`.
- **`infra/aws/README.md`:**
  - «Puesta en marcha»: sin destinatarios de prueba;
  - «Puesta en marcha», paso 6: cuota real;
  - «Observabilidad y alertas»: la alarma nueva.

**No incluye**
- Cambiar cómo la API envía el correo (sigue en segundo plano) ni reintentos automáticos: el usuario puede pedir el reenvío (HU-26).

## 3. Requisitos técnicos

- `make tf-plan` antes de aplicar: solo deben desaparecer las identidades de prueba y cambiar la política del rol y lo de observabilidad.
- Las direcciones reales de prueba no se escriben en el repositorio.
- El mensaje del filtro debe coincidir con el de `send_in_background`; comprobarlo con `aws logs test-metric-filter`.

## 4. Criterios de aceptación

**AC1 — Correo en cualquier dirección (HU-40 AC1)**
- **Given** el correo por Brevo (TK-098)
- **When** me registro en `https://entrevecinos.org` con dos direcciones no verificadas de proveedores distintos
- **Then** las dos reciben el enlace en la bandeja de entrada, autenticado con SPF, DKIM y DMARC, y validan la cuenta

**AC2 — Aviso del primer fallo (HU-40 AC2)**
- **Given** la alarma `email-send-failures`
- **When** fuerzo su estado a `ALARM` (`aws cloudwatch set-alarm-state`) o un envío falla
- **Then** recibo el aviso y otro al volver a `OK`

**AC3 — Sin restos del *sandbox* (HU-40 AC3)**
- **Given** la infraestructura aplicada
- **When** listo las identidades de SES y la política del rol de la instancia
- **Then** solo queda la identidad `entrevecinos.org` y el permiso de envío no incluye direcciones de prueba

**AC4 — Rebotes**
- **Given** el correo por Brevo
- **When** me registro con una dirección inexistente
- **Then** Brevo registra el rebote y la alarma de fallos de envío no salta (el servidor aceptó el correo)

## 5. Plan de tareas

1. `ses_test_recipients` vacío y permisos del rol.
2. Filtro de métricas, alarma, panel y *runbook*.
3. `make tf-lint`, `make tf-plan` y `make tf-apply`.
4. Pruebas de rebote y registros reales.
5. Documentación.

## 6. Verificación

```bash
aws sesv2 list-email-identities --profile entrevecinos --query 'EmailIdentities[].IdentityName'
aws logs test-metric-filter --profile entrevecinos --filter-pattern '"No se pudo enviar el correo"' \
  --log-event-messages 'No se pudo enviar el correo «Confirma tu correo»'
aws cloudwatch set-alarm-state --profile entrevecinos --alarm-name entrevecinos-prod-email-send-failures \
  --state-value ALARM --state-reason "Prueba de aviso"
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Ninguna dirección real en el repositorio.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Correo no deseado:** un dominio nuevo puede caer en *spam* al principio aunque esté autenticado. Si pasa, revisar la política DMARC (`p=none` → `quarantine` cuando haya historial) y el contenido del correo.
- **Límite de Brevo:** al pasar de 300 envíos al día, Brevo rechaza el envío; esta alarma lo detecta.
- **Alarma ruidosa:** un proveedor que rechaza una dirección inexistente cuenta como rebote, no como fallo de envío, así que no dispara esta alarma.
