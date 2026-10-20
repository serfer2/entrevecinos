## Context

Guía oficial de Next.js 16 «Content Security Policy»: el *Proxy* genera un *nonce*, lo pone en la cabecera `Content-Security-Policy` de la petición (de ahí lo extrae Next al renderizar) y de la respuesta.

## Goals / Non-Goals

**Goals:** sin `unsafe-inline` ni `unsafe-eval` en producción; imágenes del almacenamiento permitidas; nada roto en desarrollo.

**Non-Goals:** informes de violaciones (`report-to`).

## Decisions

- **CSP en `proxy.ts`, no en `next.config.ts`:** `headers()` no puede variar por petición. El resto de cabeceras de TK-003 se quedan en `next.config.ts`.
- **`storageOrigin = new URL(STORAGE_PUBLIC_URL).origin`**, calculado al cargar el *Proxy*: si falta o no es una URL, falla al arrancar (mejor que bloquear todas las imágenes en silencio).
- **Desarrollo:** `'unsafe-eval'` en scripts, `'unsafe-inline'` en estilos y `ws:` en `connect-src` (recarga en caliente); **producción:** estilos con *nonce*; `upgrade-insecure-requests` solo si el almacenamiento es HTTPS (con `http://localhost:9000` rompería las imágenes al probar la imagen de producción en local).
- **`await connection()` en el *layout* raíz** fuerza el renderizado por petición de todas las páginas.

## Risks / Trade-offs

- [Sin páginas estáticas] → aceptable en el MVP (casi todas dependen de la sesión).
- [Una CDN de imágenes en producción] → `STORAGE_PUBLIC_URL` debe apuntar a ella.
