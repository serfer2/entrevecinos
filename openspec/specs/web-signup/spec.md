# web-signup Specification

## Purpose
Registro desde el navegador (`/registro`) con validación en servidor y sesión en la cookie httpOnly `ev_session`.
## Requirements
### Requirement: Registro desde el navegador
La página `/registro` SHALL permitir crear una cuenta con nombre, correo, contraseña y teléfono opcional y, al terminar, sustituir el formulario por un aviso (`role="status"`): «Te hemos enviado un correo a {email}. Abre el enlace que contiene para activar tu cuenta. El enlace caduca en 24 horas.» y «Si no lo ves, revisa la carpeta de correo no deseado.». El registro MUST NOT crear la *cookie* `ev_session`.

#### Scenario: Registro correcto
- **WHEN** se envía el formulario con datos válidos y un correo no registrado
- **THEN** se muestra el aviso con el correo, no hay *cookie* `ev_session` y el usuario sigue en `/registro`

### Requirement: Correo ya registrado
El formulario SHALL mostrar «Este correo ya está en uso.» bajo el campo de correo cuando la API responda `409`, conservando nombre, correo y teléfono.

#### Scenario: Correo repetido
- **WHEN** se envía un correo ya registrado
- **THEN** se muestra el error bajo el correo, no se crea la *cookie* y los campos (salvo la contraseña) siguen rellenos

### Requirement: Validación en el servidor
La *Server Action* MUST validar los datos antes de llamar a la API y devolver un mensaje por campo incorrecto.

#### Scenario: Datos inválidos sin validación del navegador
- **WHEN** se envía un correo mal formado, un nombre vacío o una contraseña de menos de 12 caracteres
- **THEN** se muestra un error junto a cada campo y no se llama a la API

### Requirement: API no disponible
Ante errores de red o `5xx`, el formulario SHALL mostrar un error general (`role="alert"`) y conservar los datos salvo la contraseña.

#### Scenario: API caída
- **WHEN** la API no responde y se envía un formulario válido
- **THEN** se muestra «No se pudo crear la cuenta. Inténtalo de nuevo.»

### Requirement: Token fuera del navegador
El token MUST NOT llegar al JavaScript del navegador: el cliente de la API y la sesión solo se importan en el servidor (`server-only`).

#### Scenario: Calidad
- **WHEN** se ejecutan `lint`, `typecheck`, `test` y `build`
- **THEN** todos pasan y ningún componente de cliente importa `lib/api/server.ts` ni `features/auth/session.ts`

