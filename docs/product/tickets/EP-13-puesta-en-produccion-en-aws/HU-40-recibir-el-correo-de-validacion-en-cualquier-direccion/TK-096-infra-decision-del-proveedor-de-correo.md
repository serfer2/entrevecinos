# TK-096 · Infraestructura: decisión del proveedor de correo de producción (Brevo en lugar de SES)

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / decisión |
| **Componente** | Cuenta de Brevo (alta manual), cuenta de SES en `eu-north-1`, `infra/aws/README.md` («Decisiones de arquitectura», «Puesta en marcha») |
| **Historia** | HU-40 Recibir el correo de validación en cualquier dirección (Épica 13) |
| **Prioridad** | Alta (bloquea el registro de vecinos reales) |
| **Depende de** | TK-083, TK-084 |
| **Referencias** | TK-083 (SES y *configuration set*); TK-084 (DKIM, SPF y DMARC); [Brevo: servidor SMTP gratuito](https://www.brevo.com/free-smtp-server); [SES: acceso de producción](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El 2026-11-06 se pidió el acceso de producción de SES con `aws sesv2 put-account-details`. Ese mismo día, `aws sesv2 get-account` en `eu-north-1` devuelve:

| Campo | Valor |
|---|---|
| `ProductionAccessEnabled` | `false` |
| `Details.ReviewDetails.Status` | `GRANTED`, sin `CaseId` |
| `SendQuota` | 200 correos en 24 horas, 1 por segundo |

La cuenta está en el plan FREE de AWS. La documentación no explica que una revisión concedida no tenga efecto. Salir del *sandbox* depende de un caso de soporte de plazo incierto o de pasar al plan de pago. Mientras tanto, solo reciben correo las direcciones verificadas: nadie más puede activar su cuenta.

Se comparan los proveedores SMTP transaccionales, con el coste como primer criterio y la facilidad de integración como segundo. Resultado:

| Proveedor | Gratis | Si se supera | Motivo |
|---|---|---|---|
| **Brevo** (elegido) | 300 al día (≈ 9.000 al mes) | ≈ 9 USD/mes (5.000 correos) | El margen gratuito más amplio, empresa y datos en la UE, SMTP con STARTTLS |
| Resend | 100 al día, 3.000 al mes | 20 USD/mes | Más fácil de integrar, pero los datos de la cuenta se guardan en EE. UU. |
| Scaleway TEM | 300 al mes | 0,25 € por 1.000 | En la UE, pero otra cuenta cloud y cuota gratuita mensual baja |

Descartados: Mailjet (el plan gratuito lleva su logo), SMTP2GO (1.000 al mes), Mailgun (100 al día), Postmark (100 al mes) y SendGrid (sin plan gratuito).

**Objetivo:** cuenta de Brevo lista para enviar como `no-reply@entrevecinos.org`, comprobado que el plan gratuito sirve para producción y decisión registrada. La integración es TK-098.

## 2. Alcance

**Incluye**
- **Alta en Brevo** con el correo del proyecto, plan gratuito, sin tarjeta. Activar el envío transaccional (SMTP): Brevo puede pedir datos de la empresa o revisar la cuenta antes de activarlo.
- **Comprobaciones del plan gratuito:**
  - **límites:** 300 al día, por SMTP;
  - **datos y RGPD:** contrato de tratamiento de datos (DPA) de Brevo y ubicación de los datos.
  - Una posible marca de Brevo en el pie del correo transaccional se acepta en esta fase (decisión del 2026-11-06).
- **Credenciales SMTP:** la clave SMTP propia (no la de la API) y el usuario de SMTP. Se crean en Brevo, se guardan directamente en Parameter Store (TK-098) y nunca en el repositorio, en el chat ni en ficheros.
- **Decisión** en `infra/aws/README.md`, «Decisiones de arquitectura»:
  - nueva entrada «Correo transaccional con Brevo en lugar de SES (TK-096)», con el estado de SES, la comparación anterior, el coste, los riesgos y cómo volver a SES;
  - fila «Correo» en la tabla resumen.
- **Paso 6 de «Puesta en marcha»**: el estado real de SES en lugar de «revisión `GRANTED`», y el alta en Brevo.
- **SES se conserva** sin coste: identidad del dominio, DKIM, `MAIL FROM` y *configuration set`, como vuelta atrás. Si AWS concede el acceso más adelante, volver es solo configuración (TK-098). Opcional: abrir el caso de soporte para que quede registrado, sin bloquear nada.

**No incluye**
- Registros DNS, secretos, red ni Compose: TK-098.

## 3. Requisitos técnicos

- La clave SMTP solo en Parameter Store como `SecureString`; el usuario de SMTP, también (identifica la cuenta).
- El alta y la activación son manuales: Brevo no tiene proveedor oficial de Terraform para la cuenta.

## 4. Criterios de aceptación

**AC1 — Cuenta lista**
- **Given** la cuenta de Brevo
- **When** reviso su configuración
- **Then** el envío transaccional (SMTP) está activo en el plan gratuito y hay una clave SMTP creada para producción

**AC2 — Dominio preparado**
- **Given** la cuenta de Brevo
- **When** consulto el dominio `entrevecinos.org`
- **Then** Brevo ha dado los registros de autenticación y de marca, con el prefijo `send`, que crea TK-098

**AC3 — Decisión documentada (HU-40 AC4)**
- **Given** `infra/aws/README.md`
- **When** consulto «Decisiones de arquitectura» y el paso 6 de «Puesta en marcha»
- **Then** encuentro por qué Brevo y no SES, el coste, los límites, el estado real de SES y cómo volver a SES

## 5. Plan de tareas

1. Alta en Brevo y activación del envío transaccional.
2. Límites y DPA; registros DNS del dominio en Brevo (prefijo `send`).
3. Clave SMTP de producción (se guarda en TK-098).
4. Decisión y paso 6 en `infra/aws/README.md`.

## 6. Verificación

```bash
aws sesv2 get-account --profile entrevecinos --region eu-north-1 \
  --query '{prod:ProductionAccessEnabled,cuota:SendQuota.Max24HourSend}'   # estado de SES que se documenta
```

En Brevo: *Transactional* → *Settings* (SMTP activo) y *SMTP & API* → *SMTP keys*.

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Marca en el plan gratuito:** puede aparecer un pie de Brevo; se acepta por ahora.
- **Activación de la cuenta:** Brevo puede tardar en activar el SMTP o pedir más información.
- **Dependencia externa:** una cuenta fuera de AWS y de Terraform, con sus propios límites (300 al día) y disponibilidad. La alarma de fallos de envío (TK-097) avisa si se agotan.
- **Volumen:** por encima de 300 al día hay que pasar a un plan de pago (≈ 9 USD/mes) dentro del límite de gasto, o volver a SES si ya tiene acceso de producción.
