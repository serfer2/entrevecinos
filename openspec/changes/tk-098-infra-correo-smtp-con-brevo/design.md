## Context

TK-096 dejó la cuenta de Brevo, las credenciales en Parameter Store y los 7 registros DNS. La API ya admite SMTP; SES sigue configurado.

## Goals / Non-Goals

**Goals:** enviar por Brevo con el dominio autenticado y sin credenciales fuera de Parameter Store. **Non-Goals:** quitar SES, webhooks de Brevo, límites de envío (TK-099) y alarma de fallos (TK-097).

## Decisions

- **Valores de Brevo en `envs/prod/main.tf`**, versionados: son públicos (acaban en DNS) y así el entorno se reproduce sin `prod.tfvars`.
- **TXT de la raíz compartido** mediante `root_txt_records`: Route 53 no admite dos conjuntos TXT con el mismo nombre.
- **DMARC combinado** (`dmarc_rua`) en lugar del que propone Brevo, para no perder la alineación estricta de DKIM.
- **Origen de CloudFront desde `aws_eip.public_dns`**: `aws_instance.public_dns` no se actualiza en el mismo `apply` que asocia la IP.
- **Credenciales fuera de Terraform**: creadas a mano en Parameter Store; `deploy.sh` las añade a su única lectura.
- **Verificación TLS en el adaptador:** `smtplib.starttls()` sin contexto no verifica el servidor (comprobado en Python 3.12); se pasa `ssl.create_default_context()`.
- **SES intacto** como vuelta atrás: identidad, DKIM, MAIL FROM y permiso de envío.

## Risks / Trade-offs

- **Salida 587 a cualquier destino** (Brevo no publica rangos): solo la API tiene la red `egress`.
- **La IP pública cambia una vez** al asociar la IP elástica, y CloudFront cambia de origen en el mismo `apply`.
- **IP autorizadas fuera de Terraform:** si la IP cambiara, el correo fallaría hasta actualizar Brevo.
