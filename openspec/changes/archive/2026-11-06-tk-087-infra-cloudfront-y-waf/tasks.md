## 1. Plan Free

- [x] 1.1 Comprobar el plan Free: soporte en Terraform (`aws_pricingplanmanager_subscription`) y permisos del proyecto (`explicitDeny` de la política de control de servicios) → alternativa sin WAF

## 2. Terraform

- [x] 2.1 Módulo `edge`: distribución, comportamientos, CloudFront Function de `www` y registros alias
- [x] 2.2 Límites por IP del visitante en el proxy (`limit_req`, `429`) y registro con su IP; prueba local
- [x] 2.3 Registros estándar de acceso a CloudWatch Logs
- [x] 2.4 Módulo y salidas en `envs/prod`; `make tf-lint` sin errores
- [x] 2.5 `make tf-apply` y despliegue nuevo con los mismos *digests* (proxy)

## 3. Documentación

- [x] 3.1 `infra/aws/README.md`: «Puesta en marcha», «Web pública», «Operación», «Costes» y «Decisiones de arquitectura»

## 4. Verificación

- [x] 4.1 DNS, HTTPS, redirección de `www` y cabecera de la web (AC1)
- [x] 4.2 Origen protegido (AC3) y estáticos en caché (AC5)
- [x] 4.3 Recorrido principal con dos fotografías, sin violaciones de CSP (AC2); ajustes si hacen falta
- [x] 4.4 `429` del proxy al superar el límite de `POST` a `/iniciar-sesion`, visible en `/entrevecinos/prod/app/proxy` (AC4)
- [x] 4.5 `make tf-plan` sin cambios
- [x] 4.6 Solicitud de salida del *sandbox* de SES (procedimiento de TK-083; `--contact-language EN`): revisión `GRANTED`
