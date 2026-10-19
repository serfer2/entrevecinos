## Context

TK-009 dejó `requireUser()` y TK-010 `PATCH /v1/users/me`.

## Goals / Non-Goals

**Goals:** ver y editar nombre y teléfono; errores por campo; datos guardados intactos ante errores.

**Non-Goals:** avatar, contraseña, correo, navegación global.

## Decisions

- **Datos guardados y formulario por separado:** la página muestra los valores guardados (resumen) y el formulario; tras un error, el resumen sigue con los datos guardados y el formulario conserva lo escrito.
- **La acción comprueba la sesión con `requireUser()`** y obtiene el token con `getSessionToken()`; el DTO de usuario nunca incluye el token.
- **`revalidatePath("/perfil")` tras guardar:** el resumen se vuelve a renderizar con los datos nuevos.
- **`ProfileForm` recibe la acción por *props*** (mismo patrón que `SignupForm` y `LoginForm`).
- **`401` en la acción → redirección a sesión caducada** (token caducado entre la carga de la página y el envío).

## Risks / Trade-offs

- [Reglas duplicadas con `UserUpdateRequest`] → mismas cotas y patrón de teléfono.
