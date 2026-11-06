## Why

HU-40: SES sigue en *sandbox* en `eu-north-1` (revisión `GRANTED` pero `ProductionAccessEnabled=false`, plan FREE) y solo entrega a direcciones verificadas, así que los vecinos no pueden validar su cuenta. Hay que elegir otro proveedor y dejar la decisión registrada. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-40-recibir-el-correo-de-validacion-en-cualquier-direccion/TK-096-infra-decision-del-proveedor-de-correo.md`.

## What Changes

- Decisión: correo de producción por SMTP con Brevo (plan gratuito), con SES como vuelta atrás; comparación con Resend y Scaleway TEM por coste e integración.
- Alta manual en Brevo: cuenta, envío transaccional, dominio con prefijo de marca `send`, clave SMTP y usuario guardados en Parameter Store (`/entrevecinos/prod/smtp/{username,password}`, `SecureString`).
- `infra/aws/README.md`: paso 6 de «Puesta en marcha» con el estado real de SES y el alta en Brevo; fila «Correo» y entrada «Correo transaccional con Brevo en lugar de SES (TK-096)» en «Decisiones de arquitectura»; «Costes».

## Capabilities

### New Capabilities
- `email-provider`: proveedor de correo de producción elegido y documentado, con vuelta atrás.

### Modified Capabilities
- (ninguna)

## Impact

- Solo documentación y configuración manual fuera del repositorio: `infra/aws/README.md` («Puesta en marcha», «Decisiones de arquitectura», «Costes»). Sin cambios de Terraform, del código ni del contrato; la integración es TK-098.
