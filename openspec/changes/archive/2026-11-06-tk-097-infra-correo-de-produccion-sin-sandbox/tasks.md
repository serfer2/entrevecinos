## 1. Infraestructura

- [x] 1.1 `ses_test_recipients = []` en `prod.tfvars` (local)
- [x] 1.2 Filtro `EmailSendFailures`, alarma `email-send-failures` y panel, con el patrón probado contra el mensaje real

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «Puesta en marcha», límites reales del correo, *runbook* de la alarma y costes

## 3. Verificación

- [x] 3.1 `make tf-lint`
- [x] 3.2 `make tf-plan` y `make tf-apply`
- [x] 3.3 AC3: identidades de SES y política del rol sin destinatarios de prueba
- [x] 3.4 AC2: `set-alarm-state` a `ALARM` y vuelta a `OK` con aviso por correo
- [x] 3.5 AC4: registro con una dirección inexistente; rebote en Brevo y la alarma sin saltar
