# TK-011 · Frontend: página de perfil y edición de datos de contacto

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/profile/`, `app/(privado)/perfil/`) |
| **Historia** | HU-03 Gestionar mi perfil y datos de contacto (Épica 1) |
| **Prioridad** | Media |
| **Depende de** | TK-009, TK-010 |
| **Referencias** | `user-stories.md` HU-03; `docs/api/paths/users_me.yaml` (`get`, `patch`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-009 dejó la sesión y el DAL (`requireUser()`), y TK-010 la actualización del perfil en la API. HU-03 pide que el vecino vea su nombre, su correo y su teléfono, y que pueda editar el nombre y el teléfono, con el nombre obligatorio.

**Objetivo:** crear la página privada `/perfil` con los datos del usuario y un formulario para editar el nombre y el teléfono.

## 2. Alcance

**Incluye**
- Página `/perfil` (grupo `(privado)`) con los datos actuales.
- Esquema `profileSchema`, *Server Action* `updateProfile` y componente `ProfileForm`.
- Enlace a `/perfil` desde `/inicio`.
- Pruebas del esquema, de la acción y del formulario.

**No incluye**
- Avatar, cambio de contraseña y cambio de correo (sin soporte en la API, ver TK-010).
- Navegación global de la aplicación (cabecera y menú), que se diseñará con las pantallas de comunidades (asumido).

## 3. Requisitos técnicos

### 3.1 Estructura de ficheros

```
apps/web/src/
├── features/profile/
│   ├── schemas.ts                 # profileSchema (zod)
│   ├── actions.ts                 # "use server"; updateProfile(prevState, formData)
│   └── components/ProfileForm.tsx # "use client"; useActionState(updateProfile)
└── app/(privado)/perfil/page.tsx  # Server Component; requireUser()
```

### 3.2 Página `/perfil`

- `requireUser()` obtiene `{ full_name, email, phone }`. Sin sesión válida redirige (TK-009).
- El correo se muestra como dato de solo lectura, con la nota «El correo no se puede cambiar».
- `ProfileForm` recibe los valores actuales como *props*: solo el DTO, nunca el token.
- Si no hay teléfono, el campo aparece vacío con el texto de ayuda «Opcional. Lo verán los vecinos interesados en tus anuncios.» (asumido).

### 3.3 Validación (`profileSchema`)

| Campo | Regla | Mensaje |
|---|---|---|
| `full_name` | se recorta; de 1 a 120 caracteres | «El nombre es obligatorio.» / «Máximo 120 caracteres.» |
| `phone` | opcional; se recorta; vacío equivale a borrar; `^\+?[0-9 ()-]{6,32}$` | «Introduce un teléfono válido.» |

Mismas reglas que `UserUpdateRequest` (TK-010).

### 3.4 *Server Action* `updateProfile`

1. `requireUser()`, para comprobar la sesión también en la acción, y no solo en la página.
2. Valida con `profileSchema`. Si hay errores, devuelve `fieldErrors` y los valores introducidos.
3. Envía `PATCH /v1/users/me` con `full_name` y con `phone` (`null` si está vacío).
4. `200`: `revalidatePath("/perfil")` y devuelve `{ success: "Perfil actualizado." }`.
5. `401`: redirige a `/iniciar-sesion?motivo=sesion-caducada`.
6. `422`: errores por campo según `loc`.
7. Error de red o `5xx`: `formError = "No se pudieron guardar los cambios. Inténtalo de nuevo."`.

Cuando hay error, la página sigue mostrando los datos guardados y el formulario conserva lo que había escrito el usuario, para que pueda corregirlo (HU-03 AC3).

### 3.5 Formulario (`ProfileForm`)

- Campos: nombre (`autocomplete="name"`, `required`) y teléfono (`type="tel"`, `autocomplete="tel"`).
- Errores bajo cada campo, con `aria-invalid` y `aria-describedby`. El mensaje de éxito se anuncia con `role="status"` y el error general con `role="alert"`.
- El botón «Guardar cambios» se desactiva mientras se envía el formulario.

### 3.6 Pruebas

- `schemas.test.ts`: nombre vacío o solo con espacios, nombre demasiado largo, teléfonos válidos e inválidos, teléfono vacío.
- `actions.test.ts`: con `apiFetch` simulado, casos `200` (llama a `revalidatePath` y devuelve el mensaje de éxito), `422`, `401` (redirige) y error de red. Comprobar que `phone: ""` se envía como `null`.
- `ProfileForm.test.tsx`: valores iniciales, errores por campo y mensaje de éxito.

## 4. Criterios de aceptación

**AC1 — Consulta del perfil (HU-03 AC1)**

- **Given** que he iniciado sesión
- **When** abro `/perfil`, directamente o desde el enlace de `/inicio`
- **Then** veo mi nombre, mi correo (no editable) y mi teléfono, o el campo vacío si no lo tengo

**AC2 — Edición correcta (HU-03 AC2)**

- **Given** que estoy en `/perfil`
- **When** cambio mi nombre o mi teléfono y pulso «Guardar cambios»
- **Then** veo «Perfil actualizado.», la página muestra los datos nuevos, y al recargar o abrir `/inicio` aparece el nombre actualizado

**AC3 — Nombre obligatorio (HU-03 AC3)**

- **Given** que estoy en `/perfil`
- **When** dejo el nombre vacío o solo con espacios y guardo (incluso con la validación del navegador desactivada)
- **Then** veo «El nombre es obligatorio.» bajo el campo, no se llama a la API y, al recargar, se mantienen los datos anteriores

**AC4 — Borrar el teléfono**

- **Given** que tengo un teléfono guardado
- **When** vacío el campo y guardo
- **Then** el teléfono se elimina y el campo aparece vacío al recargar

**AC5 — Sesión requerida**

- **Given** que no he iniciado sesión, o que mi sesión ha caducado
- **When** abro `/perfil` o envío el formulario
- **Then** se me redirige a `/iniciar-sesion`: sin sesión, con `next=/perfil`, para volver a `/perfil` tras iniciar sesión; con la sesión caducada, con el aviso correspondiente (TK-009 §3.4)

## 5. Plan de tareas

1. Implementar `profileSchema` y sus pruebas.
2. Implementar la *Server Action* `updateProfile` y sus pruebas.
3. Implementar `ProfileForm` y la página `/perfil`.
4. Añadir el enlace «Mi perfil» en `/inicio`.
5. Verificar según la sección 6.

## 6. Verificación

```bash
make dev
# Navegador, con sesión iniciada:
#   /inicio → «Mi perfil» → /perfil con nombre, correo y teléfono
#   cambiar el nombre y guardar → «Perfil actualizado.»; /inicio muestra el nombre nuevo
#   nombre "   " con novalidate → error bajo el campo; al recargar se mantiene el nombre anterior
#   vaciar el teléfono y guardar → al recargar, el campo está vacío
# Sin sesión (ventana privada): /perfil → /iniciar-sesion?next=%2Fperfil
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] La página se puede usar con teclado y es responsive.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **«En mis anuncios» (HU-03 AC2):** se cumplirá cuando existan los anuncios, siempre que muestren los datos del anunciante desde el usuario (ver TK-010 §3.3).
- **Reglas duplicadas:** `profileSchema` repite las validaciones de TK-010. Mismo riesgo que en TK-007.
- **Teléfono público:** pendiente de decidir quién puede verlo (HU-14 y HU-15). El texto de ayuda de §3.2 debe ajustarse cuando se decida.
