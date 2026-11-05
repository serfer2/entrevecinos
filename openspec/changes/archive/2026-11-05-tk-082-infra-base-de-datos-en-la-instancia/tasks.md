## 1. Infraestructura

- [x] 1.1 Volumen EBS, rol y política de Data Lifecycle Manager
- [x] 1.2 Bucket de copias con la política que deniega el borrado
- [x] 1.3 Contraseñas `SecureString` (`ephemeral` + `value_wo`) y parámetros de conexión
- [x] 1.4 `infra/prod/initdb/10-roles.sh`, con prueba local de privilegios, migraciones y rotación
- [x] 1.5 `infra/prod/backup.sh` y unidades `systemd`; `shellcheck` sin avisos

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «Secretos», «Operación» (base de datos y copias) y decisión en «Decisiones de arquitectura»

## 3. Aplicación en AWS

- [x] 3.1 `make tf-apply`; comprobación del volumen (cifrado, zona), de la política de *snapshots* y de los parámetros
- [x] 3.2 Comprobación de que un principal ajeno a `admin_role_arns` no puede borrar en el bucket de copias

## 4. Verificación

- [x] 4.1 `make tf-lint` sin errores
- [x] 4.2 Segundo `make tf-plan` sin cambios
