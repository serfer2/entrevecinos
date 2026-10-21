## RENAMED Requirements

- FROM: `### Requirement: Página marcador en Compose`
- TO: `### Requirement: Servicio web en Compose`

## MODIFIED Requirements

### Requirement: Servicio web en Compose
El servicio `web` SHALL construirse desde `apps/web/Dockerfile` (etapa `dev`), depender de `api` sano, estar solo en la red `edge` y publicar `${WEB_PORT:-3000}`; su raíz SHALL llevar a una pantalla de la aplicación (ver `web-session`).

#### Scenario: Arranque del contenedor
- **WHEN** se ejecuta `docker compose --env-file .env -f infra/docker-compose.yml up -d --build web`
- **THEN** el contenedor `web` queda `healthy` y `http://localhost:3000` redirige a `/iniciar-sesion`, que devuelve 200
