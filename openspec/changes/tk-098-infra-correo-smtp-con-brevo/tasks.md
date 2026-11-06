## 1. Infraestructura

- [x] 1.1 Registros de Brevo: TXT de la raíz, DMARC y CNAME (`modules/domain`, `modules/mail/brevo.tf`, `envs/prod`)
- [x] 1.2 IP elástica, origen de CloudFront y salida `instance_public_ip` (`modules/compute`)
- [x] 1.3 Salida TCP 587 (`modules/network`)
- [x] 1.4 Compose de producción con SMTP de Brevo y `deploy.sh` con las credenciales SMTP

## 2. Backend

- [x] 2.1 STARTTLS con verificación del certificado en `SmtpEmailSender`, con pruebas

## 3. Documentación

- [x] 3.1 `infra/aws/README.md`: estructura, DNS, secretos, instancia, *runbook* de correo y destrucción

## 4. Verificación

- [x] 4.1 `make shellcheck`, `make tf-lint` y pruebas de la API
- [x] 4.2 `make tf-plan` revisado y `make tf-apply`
- [ ] 4.3 En Brevo: IP elástica autorizada, dominio verificado y seguimiento de clics desactivado
- [ ] 4.4 Despliegue y registro de extremo a extremo con dos direcciones no verificadas (cabeceras DKIM y DMARC); retirar la IP antigua de Brevo
