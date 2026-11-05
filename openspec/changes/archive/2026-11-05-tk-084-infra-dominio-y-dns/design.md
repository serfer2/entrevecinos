## Context

El dominio sigue registrado en Dinahosting; solo su DNS pasa a Route 53. La fase 0 (renovación automática, bloqueo de transferencia y DNSSEC desactivado) ya está hecha. Los registros de la web (alias a CloudFront) llegan en TK-087.

## Goals / Non-Goals

**Goals:** zona con todos los registros en Terraform; certificado emitido y dominio de SES verificado sin pasos manuales salvo la delegación.

**Non-Goals:** registros de la web y CloudFront (TK-087); DNSSEC; transferir el registro del dominio; buzón de entrada.

## Decisions

- **Dos `apply`:** el primero crea zona, registros, certificado e identidad sin esperar; tras delegar, `wait_for_certificate_validation = true` añade `aws_acm_certificate_validation` (espera hasta 2 h). Así el primer `apply` no se bloquea mientras los servidores de nombres siguen en Dinahosting.
- **Identidad de SES en `modules/mail`** con la zona como entrada: el correo queda junto al *configuration set*; `modules/domain` solo sabe de DNS y del certificado.
- **DKIM con `count = 3`:** SES siempre devuelve 3 *tokens*; un `for_each` sobre ellos no se puede planificar porque se conocen tras el `apply`.
- **TTL 300** (`dns_ttl`) durante la puesta en marcha; subirlo a 3600 cuando esté estable.
- **DMARC `p=none; adkim=s; aspf=r`:** observación primero; el DKIM de SES firma con el dominio exacto y el MAIL FROM es el subdominio `mail.`.
- **`CAA` solo de Amazon** y `issuewild ";"`: ninguna otra autoridad puede emitir certificados ni comodines.
- **Sin DNSSEC ni registro de consultas** (checkov `CKV2_AWS_38` y `CKV2_AWS_39`): DNSSEC necesita una clave KMS (≈ 1 USD/mes) y se deja para la evolución; el registro de consultas añade coste sin necesidad actual.

## Risks / Trade-offs

- [Quien controle la cuenta de AWS controla el DNS] → el registro sigue en Dinahosting y se puede volver a sus servidores; `prevent_destroy` en la zona.
- [Propagación de hasta 1-2 días] → sin web publicada todavía, no afecta a usuarios.
