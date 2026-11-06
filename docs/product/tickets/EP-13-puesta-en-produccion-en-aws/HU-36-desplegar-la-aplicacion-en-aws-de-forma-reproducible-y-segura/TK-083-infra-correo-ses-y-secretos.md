# TK-083 · Infraestructura: correo con SES y secretos de la aplicación

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/mail/`, `infra/aws/modules/secrets/`, `infra/aws/envs/prod/` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-078 |
| **Referencias** | TK-056 (envío de correo), TK-058 (validación del correo), TK-081 (`SesEmailSender`); documentación de SES «Moving out of the sandbox» |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La API envía el enlace de validación del registro por correo. En producción se usará Amazon SES con el remitente `no-reply@entrevecinos.org`; el dominio se verifica con DKIM en TK-084. SES empieza en *sandbox*: solo envía a direcciones verificadas y con un límite de 200 correos al día.

La API también necesita `JWT_SECRET` (mínimo 32 caracteres), que hoy está en el `.env` local.

**Objetivo:** preparar SES (seguimiento de eventos y destinatarios de prueba), solicitar la salida del *sandbox* y guardar el secreto de los JWT en SSM Parameter Store.

## 2. Alcance

**Incluye**
- `aws_sesv2_configuration_set` `entrevecinos-prod` con:
  - envío de eventos `BOUNCE`, `COMPLAINT`, `REJECT` y `DELIVERY` a CloudWatch (métricas para las alarmas de TK-091);
  - supresión a nivel de cuenta para rebotes y quejas.
- Identidades de dirección para destinatarios de prueba, opcionales (variable lista `ses_test_recipients`) para poder probar el registro mientras dure el *sandbox*.
- Procedimiento documentado de **solicitud de salida del *sandbox*** (`aws sesv2 put-account-details` con tipo de correo `TRANSACTIONAL`, URL de la web y descripción del uso). Se hace a mano tras el primer despliegue, cuando `https://entrevecinos.org` ya responda (TK-087).
- Parameter Store: parámetro `SecureString` `/entrevecinos/prod/jwt-secret` (nivel estándar, gratuito; cifrado con la clave gestionada `aws/ssm`), de 64 caracteres generados con `ephemeral "random_password"` y escritos con `value_wo` / `value_wo_version` para que no queden en el estado (si la versión del proveedor no lo admite, `random_password` normal con el estado cifrado de TK-078). Sin rotación automática.
- **Convención para todos los secretos de la épica:** `SecureString` en `/entrevecinos/prod/…` (JWT, contraseñas de la base de TK-082, cabecera de origen de TK-086). No se usa Secrets Manager (0,40 USD por secreto al mes).
- Salidas: nombre del *configuration set* y nombre del parámetro.

**No incluye**
- Identidad del dominio `entrevecinos.org`, DKIM y MAIL FROM (TK-084).
- Contraseñas de la base de datos (TK-082).

## 3. Requisitos técnicos

- El rol de la instancia (TK-085) lee los parámetros con `ssm:GetParameters` y `WithDecryption`; con la clave gestionada `aws/ssm` no hace falta conceder `kms:Decrypt` aparte (comprobar al implementar).
- La política del rol de la instancia (TK-085) restringirá `ses:SendEmail` a la identidad de TK-084 y a este *configuration set*.

## 4. Criterios de aceptación

**AC1 — Eventos de envío**
- **Given** el *configuration set* creado
- **When** consulto sus destinos de eventos
- **Then** rebotes, quejas, rechazos y entregas se publican como métricas de CloudWatch

**AC2 — Destinatarios de prueba**
- **Given** las direcciones de `ses_test_recipients` y sus correos de verificación confirmados
- **When** consulto sus identidades en SES
- **Then** están verificadas y podrán recibir el correo de validación mientras dure el *sandbox* (el envío real se comprueba en TK-084 AC3)

**AC3 — Secreto de los JWT (HU-36 AC4)**
- **Given** el secreto creado
- **When** busco su valor en el repositorio
- **Then** no aparece ni en el repositorio ni en el estado de Terraform; solo se puede leer desde Parameter Store

**AC4 — Solicitud de salida del *sandbox***
- **Given** la web publicada en `https://entrevecinos.org` (TK-087)
- **When** sigo el procedimiento documentado
- **Then** la solicitud queda registrada en AWS y su estado se puede consultar con `aws sesv2 get-account`

## 5. Plan de tareas

1. *Configuration set* y destinos de eventos.
2. Parámetro `SecureString` del secreto de los JWT.
3. Destinatarios de prueba y confirmación manual de sus correos.
4. Documentación del procedimiento de salida del *sandbox* (se ejecuta tras TK-087).

## 6. Verificación

```bash
make tf-apply
aws sesv2 get-configuration-set-event-destinations --configuration-set-name entrevecinos-prod --profile entrevecinos
aws sesv2 get-email-identity --email-identity <destinatario-de-prueba> --profile entrevecinos --query VerifiedForSendingStatus
aws ssm get-parameter --name /entrevecinos/prod/jwt-secret --profile entrevecinos --query 'Parameter.{t:Type,v:Version}'   # SecureString, sin mostrar el valor
aws sesv2 get-account --profile entrevecinos --query '{prod:ProductionAccessEnabled,review:Details.ReviewDetails}'
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `make tf-lint` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Rechazo de la salida del *sandbox*:** AWS revisa el sitio web y el uso previsto (correo transaccional, con gestión de rebotes y quejas); con dominio propio verificado es más probable que la apruebe. Si la deniega, solo recibirían correo las direcciones verificadas, suficiente para la demo.
- **Parameter Store frente a Secrets Manager:** decisión de coste. Se pierde la rotación gestionada (no se usaba) y la replicación entre regiones (no disponible en el plan). El nivel estándar admite valores de hasta 4 KB y 10 000 parámetros, de sobra.
- **Secreto en el estado de Terraform:** se evita con los argumentos de solo escritura; si no están disponibles, se acepta con el estado cifrado y privado.
- **Rotación de `JWT_SECRET`:** rotarlo invalida todas las sesiones; el procedimiento se documenta en TK-093.
