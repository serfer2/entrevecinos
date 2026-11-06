# aws-edge Specification

## Purpose
Web pública en `https://entrevecinos.org` con CloudFront: HTTPS, redirección de `www`, caché solo de estáticos, origen protegido por cabecera, registros de acceso y alias en Route 53.
## Requirements
### Requirement: Web en HTTPS con CloudFront
Terraform SHALL crear una distribución CloudFront con los nombres `entrevecinos.org` y `www.entrevecinos.org`, el certificado de ACM de TK-084 (SNI, `TLSv1.2_2021`), HTTP/2 y HTTP/3, IPv6 y `redirect-to-https`. Su origen MUST ser el DNS público de la instancia por HTTP en el puerto 80, con la cabecera `X-Origin-Verify` de `/entrevecinos/prod/origin-verify`, y MUST reenviar al origen el `Host`, las cookies, la *query* y las cabeceras del visitante.

#### Scenario: Redirección a HTTPS
- **WHEN** pido `http://entrevecinos.org/`
- **THEN** recibo una redirección a `https://entrevecinos.org/`

#### Scenario: Cabeceras de la web
- **WHEN** pido `https://entrevecinos.org/iniciar-sesion`
- **THEN** la respuesta incluye `Strict-Transport-Security` y la `Content-Security-Policy` de la web

### Requirement: Redirección de www
Una CloudFront Function SHALL responder `301` a toda petición a `www.entrevecinos.org` con `Location` `https://entrevecinos.org` seguido de la misma ruta y *query*.

#### Scenario: Ruta conservada
- **WHEN** pido `https://www.entrevecinos.org/iniciar-sesion?siguiente=/inicio`
- **THEN** recibo `301` con `Location: https://entrevecinos.org/iniciar-sesion?siguiente=/inicio`

### Requirement: Caché solo de estáticos
Las rutas `/_next/static/*` SHALL servirse con la política `Managed-CachingOptimized`; el resto MUST NOT cachearse (`Managed-CachingDisabled`) y MUST admitir `GET`, `HEAD`, `OPTIONS`, `PUT`, `POST`, `PATCH` y `DELETE`.

#### Scenario: Estático en caché
- **WHEN** pido dos veces el mismo fichero de `/_next/static/`
- **THEN** la segunda respuesta trae `x-cache: Hit from cloudfront`

#### Scenario: HTML sin caché
- **WHEN** pido dos veces una página
- **THEN** ninguna respuesta trae `Hit from cloudfront`

### Requirement: Registros de acceso
CloudFront SHALL enviar sus registros estándar de acceso (v2) a `/entrevecinos/prod/cloudfront` en `us-east-1`, con retención de 7 días, y MUST limitarse a los campos elegidos, sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)`.

#### Scenario: Petición registrada
- **WHEN** pido una página de la web
- **THEN** la petición aparece en `/entrevecinos/prod/cloudfront` en unos minutos

#### Scenario: Sin cadena de consulta
- **WHEN** alguien abre `/verificar-correo?token=…`
- **THEN** su registro tiene `cs-uri-stem` `/verificar-correo` y ningún campo con el *token*

### Requirement: DNS de la web
Terraform SHALL crear registros alias `A` y `AAAA` de `entrevecinos.org` y `www.entrevecinos.org` hacia la distribución en la zona de TK-084.

#### Scenario: Resolución
- **WHEN** consulto `dig A` y `dig AAAA` de `entrevecinos.org` y `www.entrevecinos.org`
- **THEN** responden direcciones de CloudFront

