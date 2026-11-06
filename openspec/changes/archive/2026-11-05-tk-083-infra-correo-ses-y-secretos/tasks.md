## 1. Infraestructura

- [x] 1.1 *Configuration set*, destino de eventos de CloudWatch y supresión de la cuenta
- [x] 1.2 Identidades de destinatarios de prueba (`ses_test_recipients`)
- [x] 1.3 Parámetro `SecureString` del secreto de los JWT con `ephemeral` y `value_wo`

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «Secretos» y procedimiento de salida del *sandbox* en «Puesta en marcha»

## 3. Aplicación en AWS

- [x] 3.1 `make tf-apply`; confirmación de los correos de verificación de los destinatarios de prueba
- [x] 3.2 Comprobación del *configuration set*, del parámetro (`SecureString`) y de que el secreto no está en el estado

## 4. Verificación

- [x] 4.1 `make tf-lint` sin errores
- [x] 4.2 Segundo `make tf-plan` sin cambios
