## ADDED Requirements

### Requirement: STARTTLS con verificación del servidor
Con `SMTP_STARTTLS=true`, el envío por SMTP SHALL negociar TLS con un contexto que verifica el certificado y el nombre del servidor, y MUST NOT usar el contexto sin verificación que `smtplib` aplica por defecto.

#### Scenario: Certificado verificado
- **WHEN** la API envía un correo por SMTP con STARTTLS
- **THEN** el contexto TLS exige un certificado válido (`CERT_REQUIRED`) y comprueba el nombre del servidor
