## 1. Estructura

- [x] 1.1 Crear `infra/` e `infra/postgres/initdb/.gitkeep`

## 2. Docker Compose

- [x] 2.1 Escribir `infra/docker-compose.yml` con el servicio `db`, el volumen `db_data` y las redes `data` (interna) y `edge`
- [x] 2.2 Escribir `infra/docker-compose.db-debug.yml` publicando solo en `127.0.0.1:${POSTGRES_HOST_PORT:-5432}`

## 3. Configuración y secretos

- [x] 3.1 Escribir `.env.example` en la raíz con valores ficticios
- [x] 3.2 Añadir `.env` a `.gitignore` (manteniendo `.env.example` versionado)

## 4. Documentación

- [x] 4.1 Redactar `infra/README.md`: levantar, parar, depurar, aviso sobre `initdb` y borrado con `down -v`

## 5. Verificación

- [x] 5.1 `docker compose config` sin advertencias y fallo sin `POSTGRES_PASSWORD` (AC3)
- [x] 5.2 `db` healthy y `select version()` devuelve 16.x (AC1)
- [x] 5.3 Persistencia tras `down`/`up` (AC2)
- [x] 5.4 Puerto 5432 no accesible desde el host; override de depuración solo en `127.0.0.1` (AC4)
- [x] 5.5 `.env` no aparece en `git status` (AC5)
