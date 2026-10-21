# TK-056 · Infra: envío de correo (SMTP) y Mailpit en desarrollo

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | `infra/docker-compose.yml`, `.env.example`, `.env` (local), `apps/api/` (configuración) |
| **Historia** | HU-25 Validar mi correo electrónico al registrarme (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-002, TK-004 |
| **Referencias** | `user-stories.md` HU-25 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La validación del correo necesita enviar emails, y el proyecto no tiene ningún servicio de correo. En desarrollo no deben salir correos reales.

**Objetivo:** que la API pueda enviar correo por SMTP y que, en desarrollo, los correos lleguen a un buzón local que se consulta desde el navegador.

## 2. Alcance

**Incluye**
- Servicio `mail` con **Mailpit** (`axllent/mailpit`, versión fijada) en `infra/docker-compose.yml`: SMTP en la red interna y la interfaz web publicada en `${MAIL_UI_HOST_PORT:-8025}`.
- Variables nuevas en `.env.example` y en `Settings` de la API.
- Las mismas variables, con los valores de desarrollo, en el `.env` local (no versionado), para que `make dev` siga funcionando sin pasos manuales.
- Dependencia `api → mail` en Compose.

**No incluye**
- El envío en sí y las plantillas (TK-058).
- Un proveedor de correo de producción: basta con apuntar las variables SMTP a él (asumido).

## 3. Requisitos técnicos

### 3.1 Compose

- `mail`: `axllent/mailpit:<versión>`, red `data` (la API llega a él como `mail:1025`), interfaz web `8025` publicada solo en `127.0.0.1`, `healthcheck` y `restart: unless-stopped` como el resto de servicios.
- Sin volumen: los correos de desarrollo se pierden al recrear el contenedor (asumido).
- `api.depends_on.mail: condition: service_healthy`.

### 3.2 Variables

| Variable | Ejemplo (desarrollo) | Uso |
|---|---|---|
| `SMTP_HOST` | `mail` | Servidor SMTP |
| `SMTP_PORT` | `1025` | Puerto SMTP |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | vacías | Credenciales (opcionales) |
| `SMTP_STARTTLS` | `false` | STARTTLS (en producción, `true`) |
| `MAIL_FROM` | `EntreVecinos <no-reply@entrevecinos.local>` | Remitente |
| `WEB_PUBLIC_URL` | `http://localhost:3000` | Origen de los enlaces que se envían por correo |
| `EMAIL_VERIFICATION_TTL_HOURS` | `24` | Caducidad del enlace de validación |
| `MAIL_UI_HOST_PORT` | `8025` | Interfaz web de Mailpit |

- `Settings`: `smtp_host`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_starttls`, `mail_from`, `web_public_url`, `email_verification_ttl_hours` (`> 0`, por defecto `24`).
- En producción, `SMTP_STARTTLS=true` y `WEB_PUBLIC_URL` con `https` (validación en `Settings`, como `environment`).

### 3.3 Make

- `make dev` levanta también `mail` y muestra su URL junto a las de `web` y `api`.

## 4. Criterios de aceptación

**AC1 — Buzón local**
- **Given** `make dev`
- **When** abro `http://localhost:8025`
- **Then** veo la interfaz de Mailpit

**AC2 — SMTP accesible desde la API**
- **Given** los servicios levantados
- **When** el contenedor `api` envía un correo de prueba a `mail:1025`
- **Then** aparece en Mailpit

**AC3 — Configuración incompleta**
- **Given** que falta `SMTP_HOST` o `WEB_PUBLIC_URL`
- **When** arranca la API
- **Then** falla al arrancar con un error de configuración

## 5. Plan de tareas

1. Servicio `mail` y dependencia en Compose.
2. Variables en `.env.example` y `Settings`.
3. Variables nuevas en el `.env` local, sin tocar los valores que ya tiene.
4. URL en la salida de `make dev`.
5. Verificación según la sección 6.

## 6. Verificación

```bash
diff <(grep -o '^[A-Z_]*=' .env.example | sort) <(grep -o '^[A-Z_]*=' .env | sort)   # sin diferencias
make dev
docker compose --env-file .env -f infra/docker-compose.yml exec api python -c \
  "import smtplib; smtplib.SMTP('mail', 1025).sendmail('a@x.test', ['b@x.test'], 'Subject: prueba\n\nhola')"
# http://localhost:8025 muestra el correo
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `make dev` funciona desde cero con el `.env.example` nuevo.
- [ ] El `.env` local tiene todas las variables de `.env.example`.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`.env` de otros entornos:** el `.env` no se versiona, así que este ticket solo actualiza el local. En el resto de copias, sin las variables nuevas la API no arrancará; hay que añadirlas (se indica en la documentación, TK-062).
