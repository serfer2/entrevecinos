## MODIFIED Requirements

### Requirement: Entorno de desarrollo completo
`make dev` SHALL construir las imágenes y levantar `db`, `mail`, `api` y `web` en segundo plano, y mostrar las URLs de la web, la API y el buzón de correo.

#### Scenario: dev
- **WHEN** se ejecuta `make dev` con los puertos por defecto
- **THEN** los servicios quedan en marcha y `http://localhost:3000`, `http://localhost:8000/docs` y `http://localhost:8025` responden
