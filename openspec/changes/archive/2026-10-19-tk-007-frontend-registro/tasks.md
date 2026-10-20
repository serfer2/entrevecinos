## 1. Base

- [x] 1.1 Dependencias (`zod`, `server-only`, Vitest y Testing Library; `@types/node` ^22), `vitest.config.mts`, `vitest.setup.ts` y script `test`
- [x] 1.2 `lib/api/server.ts` y `lib/api/errors.ts`
- [x] 1.3 `features/auth/session.ts`

## 2. Registro

- [x] 2.1 `signupSchema` y mensajes por campo, con pruebas
- [x] 2.2 *Server Action* `signup`, con pruebas (201, 409, 422, red, validación)
- [x] 2.3 `components/ui/TextField.tsx` y `SignupForm`, con pruebas
- [x] 2.4 Páginas `/registro` y `(privado)/inicio`

## 3. Documentación y verificación

- [x] 3.1 `apps/web/README.md` (sesión, pruebas, volumen de dependencias)
- [x] 3.2 `lint`, `typecheck`, `test`, `build` y verificación en navegador (TK-007 §6)
