## Context

SES no sale del *sandbox* pese a la revisión `GRANTED`; la documentación de AWS no lo explica y la cuenta está en el plan FREE.

## Goals / Non-Goals

**Goals:** proveedor elegido con datos y cuenta lista. **Non-Goals:** DNS, red y despliegue (TK-098).

## Decisions

- **Brevo por coste e integración:** 300 al día gratis, datos en la UE y SMTP con STARTTLS, que la API ya admite sin cambios de código. Resend se descarta por guardar los datos de la cuenta en EE. UU.; Scaleway, por su margen gratuito mensual.
- **SES como vuelta atrás:** no cuesta nada mantenerlo; volver es solo configuración.
- **Prefijo de marca `send`:** `mail` es el `MAIL FROM` de SES y un CNAME no puede convivir con sus registros.
- **Credenciales creadas por la persona responsable** directamente en Parameter Store, sin pasar por el agente ni por Terraform.
- **Marca de Brevo en el pie:** se acepta por ahora.

## Risks / Trade-offs

- Dependencia externa fuera de Terraform; límite de 300 al día; seguimiento de clics pendiente de desactivar antes de enviar (requisito de TK-098).
