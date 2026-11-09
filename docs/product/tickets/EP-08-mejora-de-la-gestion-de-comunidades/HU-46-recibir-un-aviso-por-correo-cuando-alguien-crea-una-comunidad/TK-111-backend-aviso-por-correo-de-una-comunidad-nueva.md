# TK-111 · Backend: aviso por correo a los administradores de plataforma cuando se crea una comunidad

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad (con documentación) |
| **Componente** | `apps/api/` (áreas `communities` y `users`, correo, cupo), `docs/api/`, `infra/aws/README.md`, `readme.md` |
| **Historia** | HU-46 Recibir un aviso por correo cuando alguien crea una comunidad (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-050, TK-052, TK-099, TK-106, TK-113 (el enlace lleva a la página que ya permite aprobar y rechazar) |
| **Referencias** | `application/communities/create_community.py` (`CreateCommunity`); `application/communities/membership_notices.py` (plantillas y cupo de TK-106); `presentation/v1/communities.py` (`create_community`); `presentation/v1/mail.py` (`send_in_background`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Desde TK-050, una comunidad creada por un vecino queda pendiente (`is_active = false`) hasta que un `platform_admin` la aprueba. Pero nadie se entera de que hay una nueva: hay que entrar en «Comunidades pendientes» para verla.

**Objetivo:** al crear una comunidad pendiente con `POST /v1/communities`, enviar un correo a cada `platform_admin` con los datos de la comunidad y de su creador y un enlace a `/admin/comunidades`. Un fallo del correo o la falta de cupo no deben impedir la creación.

## 2. Alcance

**Incluye**
- Puerto `UserRepository.list_platform_admins()` y su implementación SQLAlchemy.
- `CommunityNotices.community_created(community, creator)`, con su plantilla.
- Envío en segundo plano desde el endpoint, con el mecanismo de TK-106.
- Una plaza del cupo por aviso.
- Documentación del contrato, de `infra/aws/README.md` y de `readme.md`.

**No incluye**
- Rechazar comunidades (TK-112, TK-113).
- Avisos al creador cuando se aprueba o rechaza su comunidad (ver §8).
- Enlaces que aprueben o rechacen sin iniciar sesión (ver §8).

## 3. Requisitos técnicos

### 3.1 Cuándo se avisa

- Solo cuando la comunidad se crea pendiente (`is_active = false`). Las de un `platform_admin` se crean activas (TK-052) y no avisan (HU-46 AC4).
- Destinatarios: los usuarios con `platform_role = platform_admin`, cuenta activa y no borrada, ordenados por nombre. Cada uno recibe su propio correo (HU-46 AC3).

### 3.2 `CommunityNotices`

- Nueva clase en `application/communities/community_notices.py`, con `UserRepository`, `EmailQuota` y `web_public_url`. Mismo patrón que `MembershipNotices`: reserva una plaza por mensaje y, sin cupo, deja de preparar más.
- `community_created(community, creator) -> list[OutgoingEmail]`.
- Dependencia `CommunityNoticesDep` en `presentation/dependencies.py`.

### 3.3 Mensaje

- Asunto: «Nueva comunidad pendiente: {comunidad}».
- Texto y HTML (con `escape`):
  - Saludo con el nombre del administrador.
  - «{creador} ha creado la comunidad {comunidad} y está pendiente de aprobación.»
  - **Comunidad:** nombre, descripción («Sin descripción» si falta), ciudad, código postal («—» si faltan) y fecha de creación.
  - **Creada por:** nombre, correo, teléfono («Sin teléfono» si falta) y fecha de alta.
  - Enlace «Revisar comunidades pendientes»: `{WEB_PUBLIC_URL}/admin/comunidades#comunidad-{community_id}`. Si no hay sesión, el proxy de la web redirige al inicio de sesión con `next` y vuelve a la página (HU-46 AC2).
  - Pie: «Recibes este correo porque eres administrador de EntreVecinos.»
- Fechas en español con zona `Europe/Madrid`, en el formato que ya usen las plantillas existentes (asumido).
- El correo y el teléfono del creador sí se incluyen: los destinatarios son administradores de la plataforma y los necesitan para comprobar la comunidad (HU-46 AC1). Los avisos de TK-106 no los incluyen porque van a vecinos.

### 3.4 Endpoint

- `create_community` recibe `BackgroundTasks`, `CommunityNoticesDep` y `EmailSenderDep`. Si la comunidad creada está pendiente, prepara los avisos y los envía con `send_in_background` después de confirmar la transacción.
- La respuesta (`201` con `CommunityResponse`) no cambia.
- Un fallo del SMTP dispara la alarma `email-send-failures` (HU-46 AC5).

### 3.5 Contrato y documentación

- `docs/api/paths/communities.yaml`: la descripción del `POST` indica el aviso por correo a los `platform_admin` y su consumo de cupo. Fila TK-111 en «Cambios» de `docs/api/README.md` («sin cambios de esquema ni de respuestas»).
- `infra/aws/README.md`: estos avisos cuentan para el cupo de 5.000 correos.
- `readme.md`, MVP «Comunidades»: añadir el aviso a los administradores de plataforma junto a los de HU-43 y HU-44.
- `docs/product/user-stories.md`, «Fuera de alcance»: incluir este aviso en la lista de correos del MVP.
- `readme.md` §1.2 «Comunidades y zonas»: el administrador de la plataforma recibe un aviso por correo de cada comunidad nueva.
- `readme.md` §3.2: añadir `POST /communities` a las operaciones que usan `email_quota`.
- `apps/api/README.md`, «Comunidades»: aviso de `POST /v1/communities` a los `platform_admin` (`CommunityNotices`), destinatarios, cupo y envío en segundo plano.

### 3.6 Pruebas

- **Unitarias** (`CommunityNotices` con *fakes*):
  - un correo por `platform_admin` activo, sin los inactivos ni los borrados;
  - el contenido incluye todos los datos de AC1 y los textos alternativos de los campos vacíos;
  - el HTML va escapado;
  - una plaza por correo y, sin cupo, ningún correo más.
- **Endpoint** (`@pytest.mark.db`):
  - un vecino crea una comunidad → `201` y un correo por `platform_admin` en el *fake*;
  - un `platform_admin` crea una → `201` y ningún correo;
  - sin cupo → `201` y ningún correo.

## 4. Criterios de aceptación

**AC1 — Aviso con detalles (HU-46 AC1 y AC2)**
- **Given** un `platform_admin` y un vecino
- **When** el vecino crea una comunidad
- **Then** se recibe `201` y Mailpit recibe «Nueva comunidad pendiente: {comunidad}», dirigido al `platform_admin`, con los datos de la comunidad y del creador y el enlace a `/admin/comunidades`

**AC2 — Uno por administrador (HU-46 AC3)**
- **Given** dos `platform_admin`
- **When** se crea una comunidad pendiente
- **Then** cada uno recibe un correo distinto, dirigido solo a él

**AC3 — Sin aviso para comunidades activas (HU-46 AC4)**
- **Given** un `platform_admin`
- **When** crea una comunidad
- **Then** no se envía ningún correo

**AC4 — Sin cupo (HU-46 AC5)**
- **Given** el cupo de correos agotado
- **When** un vecino crea una comunidad
- **Then** se recibe `201`, la comunidad queda pendiente y no se envía el aviso

## 5. Plan de tareas

1. `list_platform_admins` (puerto, SQLAlchemy y *fake*).
2. `CommunityNotices` y su plantilla.
3. Envío desde `create_community`.
4. Contrato, `docs/api/README.md`, `infra/aws/README.md`, `readme.md` y `user-stories.md`.
5. Pruebas.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check . && $COMPOSE run --rm api ruff format --check .
# Con un vecino, crear una comunidad → correo al platform_admin en http://localhost:8025
# Pulsar el enlace sin sesión → inicio de sesión → «Comunidades pendientes»
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Documentación actualizada (§3.5): contrato, `docs/api/README.md`, `infra/aws/README.md`, `readme.md` (§1.2, MVP y §3.2), `apps/api/README.md` y `user-stories.md`.
- [ ] Cambios revisados y fusionados mediante *pull request*.
- [ ] Comprobado en producción con una comunidad real.

## 8. Riesgos y decisiones abiertas

- **Sin enlaces de un clic:** el correo no lleva enlaces que aprueben o rechacen sin iniciar sesión. Un enlace así necesitaría un *token* firmado de un solo uso y, si se reenviara el correo, cualquiera podría usarlo. Se prefiere llevar a la página protegida (asumido).
- **Datos personales en el correo:** el correo y el teléfono del creador salen de la aplicación hacia los buzones de los administradores de plataforma; se acepta porque son ellos quienes revisan la comunidad.
- **Coste:** un correo por `platform_admin` y por comunidad nueva. Hay pocos administradores de plataforma y una comunidad pendiente por usuario (HU-23), así que el volumen es bajo.
- **Aviso al creador:** avisar al vecino cuando aprueban o rechazan su comunidad sería otra historia, análoga a HU-44.
