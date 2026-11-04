# TK-081 · Backend: almacenamiento y correo de la API con credenciales del rol de AWS

| Campo | Valor |
|---|---|
| **Tipo** | Backend / seguridad |
| **Componente** | `apps/api/src/entrevecinos/infrastructure/` (`settings.py`, `storage/s3_object_storage.py`, `mail/`), composición en `presentation/`, `apps/api/tests/`, `.env.example`, `infra/docker-compose.yml` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-080 |
| **Referencias** | TK-019 (MinIO y URL prefirmadas), TK-056 (envío de correo por SMTP), TK-046 (CSP); guía de boto3 «Credentials» (cadena de proveedores) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La API está pensada para MinIO y Mailpit:

- `S3ObjectStorage` exige `access_key`, `secret_key` y `endpoint_url`, usa direccionamiento *path* y firma con la región `us-east-1` fija.
- El correo sale por SMTP. Con SES, SMTP necesita un usuario IAM con una clave de acceso de larga duración convertida en contraseña SMTP.

En AWS la instancia tiene un rol IAM y boto3 obtiene credenciales temporales y rotadas automáticamente del servicio de metadatos (IMDSv2). Usarlas evita guardar claves de larga duración (HU-36 AC4).

**Objetivo:** que la API funcione igual en local (MinIO, Mailpit) y en AWS (S3 y SES con el rol de la instancia), eligiendo el comportamiento solo por configuración.

## 2. Alcance

**Incluye**
- `Settings`:
  - `storage_endpoint`, `storage_public_endpoint`, `storage_access_key` y `storage_secret_key` pasan a ser opcionales (vacíos en AWS);
  - nuevos `storage_region` (por defecto `us-east-1`, MinIO lo ignora) y `storage_addressing_style` (`path` | `virtual`, por defecto `path`);
  - nuevo `mail_backend` (`smtp` | `ses`, por defecto `smtp`) y `ses_configuration_set` opcional;
  - validación: si se da una de las dos claves de almacenamiento, deben darse las dos; en `production` con `mail_backend=smtp` se mantienen las reglas actuales de STARTTLS.
- `S3ObjectStorage`: si no hay claves, no se pasan a `boto3.client` (cadena de credenciales por defecto); si no hay endpoint, se usa el de la región; si no hay endpoint público, se firma con el mismo cliente.
- `SesEmailSender` (nuevo adaptador del mismo puerto que `SmtpEmailSender`): `sesv2.send_email` con contenido simple, `FromEmailAddress = MAIL_FROM` y *configuration set* si está definido. Selección del adaptador en el punto de composición existente según `mail_backend`.
- `DATABASE_URL` de producción apunta al contenedor `db` de la red interna con el rol `entrevecinos_app` (TK-082); las migraciones usan otra URL con `entrevecinos_owner`. Si `migrations/env.py` lee la misma variable, basta con pasarla distinta al ejecutar `alembic` (TK-086); documentarlo en `.env.example`.
- Pruebas unitarias de la selección de credenciales, del firmado (región y estilo en la URL resultante) y del adaptador SES con `botocore.stub.Stubber`; pruebas de `Settings`.
- `.env.example`: variables nuevas con comentarios para local y para AWS.

**No incluye**
- Cambios en el contrato de la API (`docs/api/openapi.yaml` no cambia).
- Infraestructura de SES (TK-083) ni del rol (TK-085).

## 3. Requisitos técnicos

- Se respeta la arquitectura limpia: el nuevo adaptador vive en `infrastructure/` e implementa el puerto existente de `application/`; `tests/test_architecture.py` debe seguir pasando.
- `boto3` ya es dependencia; no se añaden paquetes.
- Con `storage_addressing_style=virtual` y sin endpoint, la URL prefirmada es `https://<bucket>.s3.eu-north-1.amazonaws.com/<clave>?X-Amz-...`; ese origen es el `STORAGE_PUBLIC_URL` de la web (CSP, TK-046).
- Los errores de SES (`MessageRejected`, `MailFromDomainNotVerified`, *throttling*) se registran sin datos personales salvo el ID de usuario (asumido) y se tratan igual que un fallo de SMTP en el flujo de registro y reenvío.
- El rol solo necesita `ses:SendEmail` sobre la identidad (TK-085).

## 4. Criterios de aceptación

**AC1 — Local sin cambios**
- **Given** el `.env` de desarrollo actual
- **When** levanto `make dev` y publico un anuncio con fotografías y me registro
- **Then** las imágenes se guardan en MinIO, se ven en el navegador y el correo llega a Mailpit

**AC2 — Credenciales del rol (HU-36 AC4)**
- **Given** la configuración de AWS sin claves de almacenamiento
- **When** la API crea el cliente de S3
- **Then** usa la cadena de credenciales por defecto de boto3 y la URL prefirmada usa la región y el estilo *virtual-hosted* configurados

**AC3 — Correo por SES**
- **Given** `MAIL_BACKEND=ses`
- **When** un vecino se registra o pide reenviar la validación
- **Then** la API llama a `SendEmail` de SES v2 con el remitente y el *configuration set* configurados

**AC4 — Configuración incoherente**
- **Given** solo una de las dos claves de almacenamiento, o `MAIL_BACKEND` con un valor no admitido
- **When** arranca la API
- **Then** falla al cargar `Settings` con un mensaje en español que indica la variable

## 5. Plan de tareas

1. `Settings` y sus pruebas.
2. `S3ObjectStorage` opcional y pruebas del firmado.
3. `SesEmailSender`, selección en la composición y pruebas con `Stubber`.
4. `.env.example`, `infra/docker-compose.yml` (sin cambios de comportamiento) y `apps/api/README.md`.

## 6. Verificación

```bash
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check . && $COMPOSE run --rm api ruff format --check .
make dev   # prueba manual de AC1
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Suite de la API, `ruff check` y `ruff format --check` sin errores.
- [ ] `.env.example` y `apps/api/README.md` actualizados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **SES por API frente a SMTP:** SMTP no requiere cambios de código, pero exige un usuario IAM con clave de larga duración (rotación manual y riesgo de fuga). La API de SES usa el rol de la instancia. Se elige la API; si se prefiere no tocar código, TK-083 crearía el usuario SMTP y su secreto.
- **Direccionamiento *path*:** AWS mantiene el estilo *path* para buckets existentes, pero lo considera obsoleto; por eso se usa *virtual-hosted* en AWS.
- **IMDSv2 desde contenedores:** las credenciales del rol llegan a los contenedores solo si el *hop limit* es 2 (TK-085).
