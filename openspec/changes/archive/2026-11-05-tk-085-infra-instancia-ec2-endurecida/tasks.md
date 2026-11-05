## 1. Infraestructura

- [x] 1.1 Rol, políticas y perfil de instancia; validación con IAM Access Analyzer
- [x] 1.2 Instancia (IMDSv2, volumen raíz, créditos `standard`, protección), adjunto del volumen de datos y *user data*
- [x] 1.3 Session Manager con registro de sesiones
- [x] 1.4 Patch Manager y alarma de recuperación
- [x] 1.5 `envs/prod`: módulo y salidas

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: acceso a la instancia, parches, recuperación, coste y decisiones

## 3. Aplicación en AWS

- [x] 3.1 `make tf-apply` y fin del *user data* (`/var/log/cloud-init-output.log`)
- [x] 3.2 Comprobaciones de AC1 a AC5 (SSH, Session Manager, IMDSv2, permisos, parches y recuperación) y del volumen montado

## 4. Verificación

- [x] 4.1 `make tf-lint` sin errores
- [x] 4.2 `make tf-plan` sin cambios
