## 1. Infraestructura

- [x] 1.1 Rutas de recuperación en el `location` con `zone=auth` del proxy
- [x] 1.2 `PASSWORD_RESET_TTL_MINUTES` en el Compose de producción
- [x] 1.3 `infra/aws/README.md`: límites, cupo, *runbook* y comprobaciones

## 2. Verificación local

- [x] 2.1 `make tf-lint`, `make shellcheck` y `nginx -t` de la plantilla

## 3. Producción (con confirmación)

- [x] 3.1 `make tf-plan` y `make tf-apply`
- [ ] 3.2 Tras desplegar: `429` en `/recuperar-contrasena`, enlace sin `token=` en los registros y recorrido completo con un correo real
