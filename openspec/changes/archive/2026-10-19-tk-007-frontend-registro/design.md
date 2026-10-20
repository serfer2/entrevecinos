## Context

TK-006 expone `POST /v1/auth/register`. El frontend no tenía cliente de API, sesión ni pruebas.

## Goals / Non-Goals

**Goals:** registro con errores por campo; el JWT nunca llega al JavaScript del navegador; base de pruebas del frontend.

**Non-Goals:** inicio de sesión, protección de rutas y DAL (TK-009); cierre de sesión.

## Decisions

- **BFF con *Server Actions*:** el navegador solo habla con Next; Next llama a la API por `API_INTERNAL_URL` y guarda el token en `ev_session` (`httpOnly`, `SameSite=Lax`, `Secure` en producción, `maxAge = expires_in`).
- **`apiFetch` sin excepciones:** devuelve un resultado discriminado (`ok`), y convierte errores de red en `status: 0`, para que las acciones decidan el mensaje.
- **`SignupForm` recibe la acción por *props*:** la página le pasa `signup`; las pruebas le pasan una acción simulada sin mockear módulos de servidor.
- **Valores conservados:** React 19 reinicia el formulario tras la acción; los campos usan `defaultValue` del estado devuelto, que nunca incluye la contraseña.
- **`TextField` en `components/ui/`:** tres formularios de la épica lo usan (registro, inicio de sesión y perfil).
- **`server-only` en pruebas:** `vitest.setup.ts` lo sustituye por un módulo vacío (fuera del entorno `react-server` lanza un error al importarse).

## Risks / Trade-offs

- [Reglas duplicadas con `RegisterRequest`] → mismas cotas que el contrato; revisar si cambia.
- [El volumen `web_node_modules` no se actualiza al cambiar dependencias] → eliminarlo y reconstruir (documentado en `apps/web/README.md`).
