## 1. Infraestructura

- [x] 1.1 Repositorios ECR y política de ciclo de vida
- [x] 1.2 Bucket de imágenes con el módulo `private-bucket` (versiones no actuales 30 días)
- [x] 1.3 Salidas (repositorios, bucket, origen público) y composición en `envs/prod`

## 2. Aplicación en AWS

- [x] 2.1 `make tf-apply`; comprobación de Block Public Access, de ECR (`IMMUTABLE`, escaneo) y de `403` sin firma

## 3. Verificación

- [x] 3.1 `make tf-lint` sin errores
- [x] 3.2 Segundo `make tf-plan` sin cambios
