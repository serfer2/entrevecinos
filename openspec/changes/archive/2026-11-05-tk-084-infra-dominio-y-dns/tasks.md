## 1. Infraestructura

- [x] 1.1 Módulo `domain`: zona alojada, SPF de la raíz, DMARC, `CAA` y salida `name_servers`
- [x] 1.2 Certificado de ACM en `us-east-1`, registros de validación y validación opcional
- [x] 1.3 `modules/mail`: identidad de dominio con DKIM, MAIL FROM y sus registros
- [x] 1.4 `envs/prod`: módulo, variables y salidas

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «DNS», delegación en «Puesta en marcha», remitente de producción y coste de la zona

## 3. Aplicación en AWS

- [x] 3.1 Primer `make tf-apply` (sin esperar la validación) y entrega de `name_servers`
- [x] 3.2 Cambio de servidores de nombres en Dinahosting (manual) y propagación
- [x] 3.3 Segundo `make tf-apply` con `wait_for_certificate_validation = true`; certificado `ISSUED` e identidad de SES verificada
- [x] 3.4 Comprobaciones con `dig` (NS, SOA, SPF, DMARC, CAA, DKIM)

## 4. Verificación

- [x] 4.1 `make tf-lint` sin errores
- [x] 4.2 `make tf-plan` sin cambios
