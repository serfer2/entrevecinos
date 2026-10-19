## 1. Rutas y redirección

- [x] 1.1 `routes.ts` (`PUBLIC_ROUTES`, `LOGIN_PATH`, `HOME_PATH`, `SESSION_COOKIE`) y uso en el registro
- [x] 1.2 `safeNextPath` con pruebas

## 2. Protección

- [x] 2.1 `src/proxy.ts` con pruebas
- [x] 2.2 DAL `getCurrentUser` y `requireUser` con pruebas

## 3. Inicio de sesión

- [x] 3.1 `loginSchema` y *Server Action* `login` con pruebas
- [x] 3.2 `LoginForm` (con pruebas) y página `/iniciar-sesion`

## 4. Páginas privadas

- [x] 4.1 `/inicio` con `requireUser()`, `error.tsx` en `(privado)`; redirección de `/registro` e `/iniciar-sesion` con sesión válida

## 5. Documentación y verificación

- [x] 5.1 README: cómo crear una página privada
- [x] 5.2 `lint`, `typecheck`, `test`, `build` y verificación en navegador (TK-009 §6)
