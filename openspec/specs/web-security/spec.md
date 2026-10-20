# web-security Specification

## Purpose
Content-Security-Policy del frontend con nonce por petición y origen de las imágenes permitido.
## Requirements
### Requirement: Content-Security-Policy con nonce
Cada página SHALL responder con una cabecera `Content-Security-Policy` que incluye `script-src 'self' 'nonce-<nonce>' 'strict-dynamic'`, un *nonce* distinto en cada petición, `object-src 'none'`, `base-uri 'self'`, `form-action 'self'` y `frame-ancestors 'none'`. En producción MUST NOT incluir `'unsafe-inline'` ni `'unsafe-eval'`.

#### Scenario: Nonce por petición
- **WHEN** se piden dos veces `/iniciar-sesion`
- **THEN** ambas respuestas tienen CSP con *nonces* distintos

### Requirement: Imágenes del almacenamiento
`img-src` SHALL incluir `'self'`, `data:` y exactamente el origen de `STORAGE_PUBLIC_URL`; si la variable falta o no es una URL, el servidor MUST fallar al arrancar.

#### Scenario: Origen local
- **WHEN** `STORAGE_PUBLIC_URL=http://localhost:9000`
- **THEN** la CSP contiene `img-src 'self' data: http://localhost:9000`

