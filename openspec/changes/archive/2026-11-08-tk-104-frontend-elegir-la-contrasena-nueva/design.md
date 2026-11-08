## Context

La validación del correo usa un *route handler* (`/verificar-correo`) que llama a la API en el `GET`, porque una página de servidor no puede escribir *cookies*. Aquí el enlace no debe consumirse en el `GET`: los escáneres de los clientes de correo abren los enlaces, y cambiar la contraseña exige un formulario.

## Goals / Non-Goals

**Goals:** recibir el enlace sin dejar el *token* en la barra de direcciones ni en el historial, cambiar la contraseña con confirmación y explicar los enlaces caducados o no válidos.

**Non-Goals:** cambiar la contraseña desde el perfil; límites por IP del proxy (TK-105).

## Decisions

- **El *token* pasa a una *cookie* `HttpOnly`** (`ev_password_reset`, `SameSite=Lax`, `Secure` fuera de desarrollo, `Path=/restablecer-contrasena`, `Max-Age` 3600) y el *route handler* redirige con `303` a la página limpia. La *cookie* solo viaja a la página y a su Server Action (mismo `Path`), nunca al JavaScript del navegador.
- **El `GET` no llama a la API:** un escáner que abra el enlace solo recibe una *cookie* que nadie usa.
- **La Server Action lee el *token* de la *cookie*, no de un campo oculto:** el *token* nunca llega al HTML.
- **Al cambiar la contraseña se borra también `ev_session`:** la API ya invalida todas las sesiones anteriores (TK-102); borrarla evita que este navegador siga con un JWT que ya no vale.
- **Mensajes del enlace en un módulo compartido** (`password-reset-link.ts`), que usan la página y el formulario: el formulario los muestra cuando la API responde `400`/`410` sin recargar.
- **La confirmación se valida en la web** (zod con `refine`): si no coinciden, no se llama a la API. La API solo recibe `password`.
- **Con sesión iniciada no se redirige:** quien abre el enlace con una sesión abierta también puede cambiar la contraseña; al terminar se cierra la sesión.

## Risks / Trade-offs

- [El enlace se abre en otro navegador distinto del que enviará el formulario] → la *cookie* vive donde se abrió el enlace; es lo esperado: hay que abrir el enlace del correo.
- [La *cookie* dura 1 hora aunque el enlace caduque antes] → la API decide la caducidad; la web solo muestra su respuesta.
