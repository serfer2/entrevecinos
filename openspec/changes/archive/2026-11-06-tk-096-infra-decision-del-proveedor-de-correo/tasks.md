## 1. Configuración manual

- [x] 1.1 Alta en Brevo y envío transaccional
- [x] 1.2 Dominio con prefijo `send` y registros DNS obtenidos
- [x] 1.3 Clave SMTP y usuario en Parameter Store (`SecureString`)

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: estado de SES, alta en Brevo, decisión, fila del resumen y costes

## 3. Verificación

- [x] 3.1 Parámetros `/entrevecinos/prod/smtp/*` de tipo `SecureString`, sin leer su valor
- [x] 3.2 Enlaces internos de la guía
