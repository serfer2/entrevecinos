# Historias de usuario del MVP — EntreVecinos

Historias del MVP definido en la sección 1.2 del `readme.md`. Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## Roles

- **Visitante**: persona sin cuenta.
- **Vecino**: usuario registrado con sesión iniciada.
- **Miembro**: vecino con acceso aprobado a una comunidad.
- **Administrador de comunidad**: persona que gestiona los miembros y los anuncios de su comunidad.
- **Administrador de plataforma** (`platform_admin`): persona que aprueba las comunidades nuevas y puede gestionar cualquier comunidad. Se nombra directamente en la base de datos (asumido).
- **Desarrollador**: persona que mantiene o evalúa el código y la documentación técnica del proyecto (asumido).

## Fuera de alcance

No se incluyen funcionalidades posteriores al MVP: perfil profesional, notificaciones automáticas, sistema completo de denuncias, panel avanzado de administración y mensajería interna. Tampoco la recuperación de contraseña, que no aparece en el README.

## Índice

| Épica | Historias |
|---|---|
| 1. Registro y perfil básico | HU-01, HU-02, HU-03 |
| 2. Comunidades | HU-04, HU-05, HU-06 |
| 3. Gestión de anuncios | HU-07, HU-08, HU-09, HU-09b |
| 4. Explorar y encontrar anuncios | HU-10, HU-11, HU-12, HU-13 |
| 5. Detalle y contacto | HU-14, HU-15 |
| 6. Administración mínima | HU-16, HU-17 |
| 7. Mejora de funcionalidades del MVP | HU-18, HU-19, HU-20 |
| 8. Mejora de la gestión de comunidades | HU-21, HU-22, HU-23 |
| 9. Cierre de sesión | HU-24 |
| 10. Validación del correo electrónico | HU-25, HU-26, HU-27 |
| 11. Experiencia de usuario | HU-28, HU-29, HU-30, HU-31, HU-32 |
| 12. Documentación técnica | HU-33 |

---

## Épica 1 — Registro y perfil básico

### HU-01 Registrarme con mi correo electrónico

**Como** visitante, **quiero** crear una cuenta con mi correo electrónico y una contraseña, **para** poder usar EntreVecinos.

**AC1 — Registro correcto**

- **Given** que no tengo cuenta y estoy en el formulario de registro
- **When** introduzco mi nombre, un correo válido no registrado y una contraseña válida y envío el formulario
- **Then** se crea mi cuenta, pendiente de validar el correo, y veo un aviso de que he recibido un correo de confirmación; la sesión se inicia al abrir el enlace (ver HU-25)

**AC2 — Correo ya registrado**

- **Given** que ya existe una cuenta con el correo `vecino@example.com`
- **When** intento registrarme con ese mismo correo
- **Then** veo un mensaje que indica que el correo ya está en uso y no se crea ninguna cuenta; si la cuenta está pendiente de validación, el mensaje lo indica y me ofrece recibir de nuevo el correo (ver HU-26)

**AC3 — Datos inválidos**

- **Given** que estoy en el formulario de registro
- **When** envío el formulario con el correo mal formado, el nombre vacío o una contraseña que no cumple los requisitos (asumido)
- **Then** veo un mensaje de error junto a cada campo incorrecto y no se crea la cuenta

### HU-02 Iniciar sesión

**Como** vecino registrado, **quiero** iniciar sesión con mi correo y contraseña, **para** acceder a mi comunidad y a mis anuncios.

**AC1 — Acceso correcto**

- **Given** que tengo una cuenta con el correo validado
- **When** introduzco mi correo y mi contraseña correctos
- **Then** accedo a la aplicación con mi sesión iniciada

**AC4 — Correo sin validar**

- **Given** que mi cuenta todavía no ha validado el correo y no soy administrador de la plataforma
- **When** introduzco mi correo y mi contraseña correctos
- **Then** no se inicia la sesión, veo que tengo que validar mi correo y puedo pedir otro correo de validación (ver HU-25 y HU-26)

**AC2 — Credenciales incorrectas**

- **Given** que estoy en la pantalla de inicio de sesión
- **When** introduzco un correo o una contraseña incorrectos
- **Then** veo un mensaje de error genérico que no revela cuál de los dos datos falló (asumido)

**AC3 — Contenido protegido**

- **Given** que no he iniciado sesión
- **When** intento acceder a los anuncios de una comunidad
- **Then** se me pide iniciar sesión antes de ver el contenido

### HU-03 Gestionar mi perfil y datos de contacto

**Como** vecino, **quiero** consultar y editar mi nombre y mis datos de contacto, **para** que otros vecinos puedan localizarme cuando les interese un anuncio mío.

**AC1 — Consulta del perfil**

- **Given** que he iniciado sesión
- **When** abro mi perfil
- **Then** veo mi nombre, mi correo electrónico y mi teléfono (asumido: el teléfono es opcional)

**AC2 — Edición correcta**

- **Given** que estoy editando mi perfil
- **When** cambio mi nombre o mi teléfono y guardo
- **Then** los datos se guardan y se muestran actualizados en mi perfil y en mis anuncios

**AC3 — Nombre obligatorio**

- **Given** que estoy editando mi perfil
- **When** dejo el nombre vacío y guardo
- **Then** veo un mensaje de error y los datos anteriores se conservan

---

## Épica 2 — Comunidades

### HU-04 Crear una comunidad

**Como** vecino, **quiero** crear una comunidad para mi urbanización o barrio, **para** que mis vecinos y yo podamos publicar anuncios en un espacio común.

**AC1 — Creación correcta**

- **Given** que he iniciado sesión
- **When** introduzco el nombre de la comunidad (y opcionalmente descripción, ciudad y código postal) y la creo
- **Then** la comunidad queda creada y yo paso a ser su administrador con acceso aprobado (asumido)

**AC2 — Nombre obligatorio**

- **Given** que estoy en el formulario de creación de comunidad
- **When** lo envío sin nombre
- **Then** veo un mensaje de error y no se crea la comunidad

**AC3 — Comunidad disponible para otros**

- **Given** que he creado una comunidad y ha sido aprobada (HU-21)
- **When** otro vecino busca comunidades
- **Then** puede encontrar la mía y solicitar el acceso

### HU-05 Seleccionar una comunidad y solicitar el acceso

**Como** vecino, **quiero** encontrar mi comunidad y solicitar unirme a ella, **para** ver sus anuncios y publicar los míos.

**AC1 — Búsqueda de comunidades**

- **Given** que he iniciado sesión y no soy miembro de ninguna comunidad
- **When** busco comunidades por nombre, ciudad o código postal (asumido)
- **Then** veo un listado de comunidades que coinciden con la búsqueda

**AC2 — Solicitud de acceso**

- **Given** que he encontrado mi comunidad
- **When** solicito unirme
- **Then** mi solicitud queda como pendiente de aprobación por un administrador

**AC3 — Sin acceso hasta la aprobación**

- **Given** que mi solicitud está pendiente
- **When** intento ver o publicar anuncios en esa comunidad
- **Then** no puedo hacerlo y veo un aviso de que mi solicitud aún no ha sido aprobada

**AC4 — Solicitud duplicada**

- **Given** que ya tengo una solicitud pendiente o soy miembro de una comunidad
- **When** intento solicitar el acceso de nuevo a la misma comunidad
- **Then** no se crea una segunda solicitud y veo mi estado actual en esa comunidad

### HU-06 Aprobar o rechazar solicitudes de acceso

**Como** administrador de comunidad, **quiero** aprobar o rechazar las solicitudes de acceso, **para** que solo entren personas de mi comunidad.

**AC1 — Ver solicitudes pendientes**

- **Given** que soy administrador de una comunidad con solicitudes pendientes
- **When** abro la gestión de miembros
- **Then** veo la lista de solicitudes pendientes con el nombre de cada solicitante

**AC2 — Aprobar**

- **Given** que hay una solicitud pendiente
- **When** la apruebo
- **Then** el solicitante pasa a ser miembro y puede ver y publicar anuncios en la comunidad

**AC3 — Rechazar**

- **Given** que hay una solicitud pendiente
- **When** la rechazo
- **Then** el solicitante no obtiene acceso y la solicitud deja de aparecer como pendiente

**AC4 — Permiso restringido**

- **Given** que soy miembro sin rol de administrador
- **When** intento acceder a la gestión de solicitudes
- **Then** no puedo verla ni resolver ninguna solicitud

---

## Épica 3 — Gestión de anuncios

### HU-07 Publicar un anuncio

**Como** miembro de una comunidad, **quiero** publicar un anuncio con su información y fotografías, **para** ofrecer o solicitar productos y servicios a mis vecinos.

**AC1 — Publicación correcta**

- **Given** que soy miembro aprobado de una comunidad
- **When** completo título, descripción, categoría y tipo (Vendo, Busco, Ofrezco, Necesito, Regalo u Otros) y publico
- **Then** el anuncio aparece en el listado de la comunidad con la fecha de publicación actual

**AC2 — Precio opcional**

- **Given** que estoy creando un anuncio
- **When** lo publico sin precio (asumido: es habitual en Regalo o Busco)
- **Then** el anuncio se publica sin precio y se muestra sin él

**AC3 — Fotografías**

- **Given** que estoy creando un anuncio
- **When** adjunto una o varias fotografías (asumido: con un máximo de imágenes y de tamaño por imagen)
- **Then** las fotografías se muestran en el anuncio

**AC4 — Campos obligatorios**

- **Given** que estoy creando un anuncio
- **When** intento publicar sin título, descripción, categoría o tipo
- **Then** veo un mensaje de error en los campos que faltan y el anuncio no se publica

**AC5 — Sin acceso aprobado**

- **Given** que no soy miembro aprobado de la comunidad
- **When** intento publicar un anuncio en ella
- **Then** no puedo hacerlo

### HU-08 Editar mis anuncios

**Como** miembro, **quiero** editar los anuncios que he publicado, **para** corregir o actualizar su información.

**AC1 — Edición correcta**

- **Given** que soy el autor de un anuncio
- **When** modifico su título, descripción, categoría, tipo, precio o fotografías y guardo
- **Then** el anuncio muestra la información actualizada

**AC2 — Validación**

- **Given** que estoy editando mi anuncio
- **When** dejo vacío el título o la descripción y guardo
- **Then** veo un mensaje de error y se conserva la versión anterior

**AC3 — Solo el autor**

- **Given** que un anuncio pertenece a otro vecino
- **When** intento editarlo
- **Then** no se me ofrece la opción de edición y no puedo modificarlo

### HU-09 Eliminar mis anuncios

**Como** miembro, **quiero** eliminar un anuncio mío, **para** retirarlo cuando ya no sea válido.

**AC1 — Confirmación**

- **Given** que soy el autor de un anuncio
- **When** elijo eliminarlo
- **Then** se me pide confirmar la acción antes de eliminarlo (asumido)

**AC2 — Eliminación correcta**

- **Given** que he confirmado la eliminación
- **When** vuelvo al listado de la comunidad
- **Then** el anuncio ya no aparece ni en el listado ni en las búsquedas

**AC3 — Solo el autor**

- **Given** que un anuncio pertenece a otro vecino
- **When** intento eliminarlo
- **Then** no se me ofrece la opción y no puedo eliminarlo (salvo que sea administrador, ver HU-17)

### HU-09b Marcar mi anuncio como reservado o finalizado

**Como** miembro, **quiero** marcar mi anuncio como reservado o finalizado, **para** que los vecinos sepan que ya no está disponible.

**AC1 — Reservar**

- **Given** que soy el autor de un anuncio activo
- **When** lo marco como reservado
- **Then** el anuncio se muestra con la etiqueta «Reservado» en el listado y en el detalle

**AC2 — Quitar la reserva**

- **Given** que soy el autor de un anuncio reservado
- **When** quito la reserva
- **Then** el anuncio vuelve a mostrarse como disponible

**AC3 — Finalizar**

- **Given** que soy el autor de un anuncio activo o reservado
- **When** lo marco como finalizado y confirmo la acción
- **Then** deja de aparecer en el listado y en las búsquedas, y ya no puedo cambiar su estado ni editarlo (asumido)

**AC4 — Solo el autor**

- **Given** que un anuncio pertenece a otro vecino
- **When** consulto su detalle
- **Then** no se me ofrecen estas opciones y no puedo cambiar su estado

---

## Épica 4 — Explorar y encontrar anuncios

### HU-10 Ver los anuncios de mi comunidad

**Como** miembro, **quiero** ver los anuncios de mi comunidad, **para** descubrir qué ofrecen y necesitan mis vecinos.

**AC1 — Listado**

- **Given** que soy miembro aprobado de una comunidad con anuncios
- **When** abro el listado de la comunidad
- **Then** veo sus anuncios con título, tipo, precio (si lo tienen), fotografía y fecha de publicación (asumido)

**AC2 — Orden por defecto**

- **Given** que abro el listado sin aplicar ninguna ordenación
- **When** se muestran los anuncios
- **Then** aparecen primero los publicados más recientemente (asumido)

**AC3 — Comunidad sin anuncios**

- **Given** que la comunidad aún no tiene anuncios
- **When** abro el listado
- **Then** veo un mensaje que lo indica y una invitación a publicar el primero (asumido)

**AC4 — Acceso restringido a miembros**

- **Given** que no soy miembro aprobado de la comunidad
- **When** intento ver su listado
- **Then** no puedo ver sus anuncios

### HU-11 Buscar anuncios por palabras clave

**Como** miembro, **quiero** buscar anuncios por palabras clave, **para** encontrar rápidamente lo que necesito.

**AC1 — Coincidencias**

- **Given** que estoy en el listado de mi comunidad
- **When** escribo una palabra clave y busco
- **Then** veo solo los anuncios cuyo título o descripción la contienen

**AC2 — Sin resultados**

- **Given** que estoy en el listado de mi comunidad
- **When** busco una palabra que no aparece en ningún anuncio
- **Then** veo un mensaje de que no hay resultados

**AC3 — Limpiar la búsqueda**

- **Given** que he aplicado una búsqueda
- **When** la borro
- **Then** vuelvo a ver todos los anuncios de la comunidad

**AC4 — Búsqueda demasiado corta**

- **Given** que estoy en el listado de mi comunidad
- **When** busco un texto de menos de 2 caracteres
- **Then** veo un mensaje que indica que la búsqueda debe tener al menos 2 caracteres y el listado no cambia

### HU-12 Filtrar anuncios por comunidad y tipo

**Como** miembro, **quiero** filtrar los anuncios por comunidad y por tipo, **para** ver solo los que me interesan.

**AC1 — Filtro por tipo**

- **Given** que estoy en el listado de mi comunidad
- **When** selecciono el tipo "Vendo"
- **Then** veo solo los anuncios de tipo "Vendo"

**AC2 — Cambio de comunidad**

- **Given** que soy miembro aprobado de más de una comunidad (asumido)
- **When** selecciono otra de mis comunidades
- **Then** veo únicamente los anuncios de esa comunidad

**AC3 — Filtros combinados**

- **Given** que he escrito una palabra clave
- **When** además selecciono un tipo
- **Then** veo solo los anuncios que cumplen ambas condiciones

### HU-13 Ordenar anuncios por fecha o precio

**Como** miembro, **quiero** ordenar los anuncios por fecha o por precio, **para** ver primero los más recientes o los más baratos.

**AC1 — Por fecha**

- **Given** que estoy en el listado de mi comunidad
- **When** ordeno por fecha de publicación
- **Then** los anuncios se muestran de más reciente a más antiguo, o al revés si invierto el orden (asumido)

**AC2 — Por precio**

- **Given** que estoy en el listado de mi comunidad
- **When** ordeno por precio
- **Then** los anuncios se muestran de menor a mayor precio, o al revés si invierto el orden (asumido)

**AC3 — Anuncios sin precio**

- **Given** que hay anuncios sin precio
- **When** ordeno por precio
- **Then** los anuncios sin precio se muestran al final del listado (asumido)

---

## Épica 5 — Detalle y contacto

### HU-14 Consultar el detalle de un anuncio

**Como** miembro, **quiero** ver la información completa de un anuncio y de quien lo publicó, **para** decidir si me interesa.

**AC1 — Información del anuncio**

- **Given** que estoy en el listado de mi comunidad
- **When** abro un anuncio
- **Then** veo su título, fotografías, descripción, categoría, tipo, precio (si lo tiene) y fecha de publicación

**AC2 — Información del anunciante**

- **Given** que estoy viendo el detalle de un anuncio
- **When** consulto la sección del anunciante
- **Then** veo su nombre y sus datos de contacto

**AC3 — Anuncio no disponible**

- **Given** que un anuncio ha sido eliminado o retirado
- **When** intento abrirlo
- **Then** veo un mensaje de que el anuncio no está disponible

### HU-15 Contactar con el anunciante

**Como** miembro interesado en un anuncio, **quiero** contactar directamente con quien lo publicó, **para** acordar la compra, el servicio o el intercambio.

**AC1 — Canal de contacto visible**

- **Given** que soy miembro aprobado y estoy en el detalle de un anuncio
- **When** elijo la opción de contactar
- **Then** se me muestran los datos de contacto directos del anunciante (teléfono y/o correo, según los que haya informado) (asumido)

**AC2 — Anunciante sin teléfono**

- **Given** que el anunciante no ha informado teléfono
- **When** elijo contactar
- **Then** se me muestra su correo electrónico como canal de contacto (asumido)

**AC3 — Datos protegidos**

- **Given** que no he iniciado sesión o no soy miembro aprobado de la comunidad
- **When** intento ver los datos de contacto de un anuncio
- **Then** no se me muestran (asumido)

---

## Épica 6 — Administración mínima

### HU-16 Gestionar los miembros de mi comunidad

**Como** administrador de comunidad, **quiero** ver y gestionar a los miembros, **para** mantener la comunidad segura y ordenada.

**AC1 — Listado de miembros**

- **Given** que soy administrador de una comunidad
- **When** abro la gestión de miembros
- **Then** veo la lista de sus miembros con su estado

**AC2 — Expulsar o bloquear**

- **Given** que un miembro incumple las normas de la comunidad
- **When** lo expulso o lo bloqueo (asumido)
- **Then** pierde el acceso a los anuncios de la comunidad, no puede publicar en ella y sus anuncios dejan de mostrarse a los demás miembros

**AC3 — Restricción a administradores**

- **Given** que soy miembro sin rol de administrador
- **When** intento gestionar miembros
- **Then** no tengo acceso a esa función

### HU-17 Retirar anuncios problemáticos

**Como** administrador de comunidad, **quiero** retirar los anuncios inapropiados, **para** que la comunidad solo muestre contenido adecuado.

**AC1 — Retirada**

- **Given** que soy administrador y hay un anuncio inapropiado en mi comunidad
- **When** lo retiro
- **Then** deja de mostrarse en el listado y en las búsquedas de la comunidad

**AC2 — Anuncio retirado no accesible**

- **Given** que un anuncio ha sido retirado por un administrador
- **When** un miembro intenta abrirlo
- **Then** ve un mensaje de que el anuncio no está disponible

**AC3 — Restricción a administradores**

- **Given** que soy miembro sin rol de administrador
- **When** intento retirar el anuncio de otro vecino
- **Then** no tengo esa opción

---

## Épica 7 — Mejora de funcionalidades del MVP

Mejoras sobre las funcionalidades ya implementadas en las épicas 1 a 6. No añade las funcionalidades posteriores al MVP descritas en «Fuera de alcance» (asumido).

### HU-18 Acceder a la aplicación desde la página principal

**Como** visitante o vecino, **quiero** que la dirección principal de EntreVecinos me lleve a una pantalla desde la que pueda empezar a usarla, **para** no quedarme en una página sin salida.

**AC1 — Sin sesión**

- **Given** que no tengo la sesión iniciada
- **When** abro la dirección principal de la aplicación
- **Then** llego al formulario de inicio de sesión, desde el que puedo ir al registro

**AC2 — Con sesión**

- **Given** que tengo la sesión iniciada
- **When** abro la dirección principal de la aplicación
- **Then** llego a mi página de inicio

### HU-19 Buscar comunidades al registrarme o iniciar sesión si no pertenezco a ninguna

**Como** vecino que todavía no pertenece a ninguna comunidad, **quiero** llegar a la lista de comunidades al registrarme o al iniciar sesión, **para** encontrar la mía y solicitar el acceso sin pasos intermedios.

**AC1 — Sin comunidades**

- **Given** que no soy miembro aprobado de ninguna comunidad (asumido: una solicitud pendiente, rechazada o un bloqueo no cuentan)
- **When** inicio sesión
- **Then** llego a la lista de comunidades existentes

**AC2 — Registro**

- **Given** que acabo de crear mi cuenta
- **When** termino el registro
- **Then** llego a la lista de comunidades existentes

**AC3 — Destino solicitado**

- **Given** que el inicio de sesión me lo pidió una ruta protegida
- **When** inicio sesión
- **Then** vuelvo a esa ruta en lugar de a la lista de comunidades (asumido)

### HU-20 Entrar en mi comunidad al iniciar sesión si solo pertenezco a una

**Como** miembro de una sola comunidad, **quiero** llegar directamente a ella al iniciar sesión, **para** ver sus anuncios sin pasos intermedios.

**AC1 — Una comunidad**

- **Given** que soy miembro aprobado de una sola comunidad
- **When** inicio sesión
- **Then** llego a esa comunidad

**AC2 — Varias comunidades**

- **Given** que soy miembro aprobado de dos o más comunidades
- **When** inicio sesión
- **Then** llego a mi página de inicio, con la lista de mis comunidades (asumido)

**AC3 — Destino solicitado**

- **Given** que el inicio de sesión me lo pidió una ruta protegida
- **When** inicio sesión
- **Then** vuelvo a esa ruta en lugar de a mi comunidad (asumido)

---

## Épica 8 — Mejora de la gestión de comunidades

Control sobre las comunidades que se crean: un administrador de plataforma las revisa antes de que estén disponibles.

### HU-21 Aprobar las comunidades nuevas antes de activarlas

**Como** administrador de plataforma, **quiero** aprobar las comunidades que crean los vecinos antes de que estén activas, **para** evitar comunidades duplicadas o falsas.

**AC1 — Comunidad pendiente**

- **Given** que soy un vecino con la sesión iniciada
- **When** creo una comunidad
- **Then** queda pendiente de aprobación: no aparece en las búsquedas, nadie puede entrar en ella ni solicitar el acceso, y yo la veo en mis comunidades como pendiente

**AC2 — Revisión**

- **Given** que soy administrador de plataforma
- **When** abro la lista de comunidades pendientes
- **Then** veo las comunidades por aprobar, de la más antigua a la más reciente, con su nombre, descripción, ubicación y fecha de creación (asumido)

**AC3 — Aprobación**

- **Given** que soy administrador de plataforma y hay una comunidad pendiente
- **When** la apruebo
- **Then** queda activa: aparece en las búsquedas y su creador entra en ella como administrador

**AC4 — Restricción**

- **Given** que no soy administrador de plataforma
- **When** intento ver las comunidades pendientes o aprobar una
- **Then** no tengo acceso a esa función

### HU-22 Activar al momento las comunidades que crea un administrador de plataforma

**Como** administrador de plataforma, **quiero** que las comunidades que creo queden activas al momento, **para** no tener que aprobar mis propias comunidades.

**AC1 — Comunidad activa**

- **Given** que soy administrador de plataforma
- **When** creo una comunidad
- **Then** queda activa, aparece en las búsquedas y entro en ella como su administrador

**AC2 — Vecinos**

- **Given** que soy un vecino sin rol de administrador de plataforma
- **When** creo una comunidad
- **Then** sigue quedando pendiente de aprobación (HU-21)

### HU-23 Tener una sola comunidad pendiente de aprobación a la vez

**Como** administrador de plataforma, **quiero** que cada vecino tenga como mucho una comunidad pendiente de aprobación, **para** que la lista de revisión no se llene de solicitudes repetidas.

**AC1 — Con una comunidad pendiente**

- **Given** que he creado una comunidad que sigue pendiente de aprobación
- **When** intento crear otra
- **Then** se me indica que ya tengo una comunidad pendiente y no se crea

**AC2 — Tras la aprobación**

- **Given** que mi comunidad pendiente ha sido aprobada
- **When** creo otra comunidad
- **Then** se crea y queda pendiente de aprobación

---

## Épica 9 — Cierre de sesión

### HU-24 Cerrar sesión

**Como** vecino con la sesión iniciada, **quiero** cerrar mi sesión, **para** que nadie más pueda usar mi cuenta desde este navegador, por ejemplo en un equipo compartido.

**AC1 — Acceso visible**

- **Given** que tengo la sesión iniciada
- **When** estoy en cualquier página de la zona privada
- **Then** tengo a mano la opción «Cerrar sesión» en la cabecera, junto a «Mi perfil» (asumido)

**AC2 — Cierre de sesión**

- **Given** que tengo la sesión iniciada
- **When** pulso «Cerrar sesión»
- **Then** mi sesión termina y voy a la raíz del sitio, que me lleva al inicio de sesión

**AC3 — Sin acceso tras cerrar**

- **Given** que he cerrado la sesión
- **When** intento abrir una página privada, también con el botón «Atrás» del navegador
- **Then** se me pide iniciar sesión

---

## Épica 10 — Validación del correo electrónico

Las cuentas nuevas solo se activan cuando su titular demuestra que controla la dirección de correo con la que se registró.

### HU-25 Validar mi correo electrónico al registrarme

**Como** visitante que se registra, **quiero** validar mi dirección de correo con un enlace que recibo por email, **para** que mi cuenta quede activa y nadie pueda registrarse con un correo que no es suyo.

**AC1 — Correo de validación**

- **Given** que no tengo cuenta y completo el registro con datos válidos
- **When** envío el formulario
- **Then** mi cuenta se crea sin activar, recibo un correo con un enlace de validación y, en lugar de entrar en la aplicación, veo un aviso de que me hemos enviado ese correo

**AC2 — Validación**

- **Given** que he recibido el correo de validación hace menos de 24 horas
- **When** visito el enlace
- **Then** mi cuenta queda activa, entro con la sesión iniciada y llego a la lista de comunidades

**AC3 — Enlace caducado**

- **Given** que el enlace de validación tiene más de 24 horas
- **When** lo visito
- **Then** veo que ha caducado, mi cuenta sigue sin activar y puedo pedir un correo nuevo (HU-26)

**AC4 — Cuenta sin validar**

- **Given** que no he validado mi correo
- **When** intento iniciar sesión con mi correo y mi contraseña correctos
- **Then** no entro y veo que tengo que validar mi correo, con la opción de recibir de nuevo el mensaje (asumido)

**AC5 — Administrador de plataforma**

- **Given** que mi cuenta es de administrador de plataforma
- **When** inicio sesión sin haber validado mi correo
- **Then** entro con normalidad

### HU-26 Recibir de nuevo el correo de validación

**Como** vecino que no ha validado su correo, **quiero** pedir que me envíen de nuevo el mensaje de validación, **para** activar mi cuenta si no me llegó, lo borré o caducó.

**AC1 — Registro con un correo pendiente**

- **Given** que ya me registré con un correo que sigue pendiente de validación
- **When** intento registrarme de nuevo con ese correo
- **Then** veo un error que me indica que el correo está pendiente de validación y la opción de recibir de nuevo el mensaje

**AC2 — Reenvío**

- **Given** que tengo una cuenta pendiente de validación
- **When** pido recibir de nuevo el mensaje
- **Then** recibo un correo nuevo con un enlace válido durante 24 horas y los enlaces anteriores dejan de funcionar

**AC3 — Sin revelar cuentas**

- **Given** que pido el reenvío para un correo que no existe o ya está validado
- **When** envío la petición
- **Then** veo el mismo aviso que en el caso anterior y no se envía ningún correo (asumido)

### HU-27 Entender por qué no funciona un enlace de validación antiguo

**Como** vecino que ha pedido varios correos de validación, **quiero** que, si abro un enlace que ya no vale, se me explique el motivo real, **para** saber qué hacer en lugar de creer que mi cuenta ya está activa.

**AC1 — Enlace sustituido por otro más reciente**

- **Given** que mi cuenta sigue pendiente de validación y he recibido un correo de validación más reciente
- **When** abro el enlace de un correo anterior sin tener la sesión iniciada
- **Then** veo que ese enlace ya no es válido porque te hemos enviado uno más reciente, con la opción de recibir de nuevo el mensaje, y no se me dice que mi correo está validado

**AC2 — Cuenta ya validada**

- **Given** que ya validé mi correo
- **When** abro de nuevo el mismo enlace o el de un correo anterior
- **Then** veo «Tu correo ya está validado. Inicia sesión.» en el inicio de sesión, o entro en la aplicación si tengo la sesión iniciada, como hasta ahora

**AC3 — Enlace desconocido**

- **Given** un enlace cuyo token no corresponde a ningún correo de validación enviado
- **When** lo abro
- **Then** veo «El enlace de validación no es válido.» y no se me dice que mi correo está validado

**AC4 — Sin revelar cuentas**

- **Given** un token que no se ha enviado nunca por correo
- **When** se usa
- **Then** la respuesta no revela si un correo está registrado ni su estado (asumido)

---

## Épica 11 — Experiencia de usuario

Mejoras de presentación y de uso sobre las funcionalidades existentes, sin añadir funcionalidad de negocio nueva.

### HU-28 Usar una interfaz sencilla, clara y con identidad propia

**Como** vecino, **quiero** una web limpia, legible y con un aspecto que transmita cercanía con la naturaleza, **para** encontrar y publicar anuncios sin esfuerzo y reconocer EntreVecinos como algo propio de mi barrio.

**AC1 — Identidad visual coherente**

- **Given** que navego por cualquier página de la aplicación
- **When** la veo en un navegador de escritorio, una tableta o un móvil
- **Then** todas usan la misma paleta (verdes suaves, tonos tierra y fondos claros), la misma tipografía y el mismo logotipo, con un contraste de texto suficiente (AA)

**AC2 — Anuncios fáciles de explorar**

- **Given** que estoy en el listado de mi comunidad
- **When** recorro los anuncios
- **Then** cada tarjeta destaca la fotografía, el título y el precio, y muestra el tipo de anuncio y si está reservado

**AC3 — Búsqueda y filtros a mano**

- **Given** que estoy en el listado de mi comunidad
- **When** quiero buscar o filtrar
- **Then** encuentro la búsqueda, los filtros y el orden agrupados en un mismo panel, encima de los anuncios

**AC4 — Adaptable**

- **Given** que uso un móvil
- **When** abro cualquier página
- **Then** el contenido se reorganiza sin desplazamiento horizontal y la cabecera no ocupa espacio fijo en la pantalla

### HU-29 Usar los formularios correctamente en cualquier navegador

**Como** vecino que usa Firefox, **quiero** que los formularios se vean igual de bien que en otros navegadores, **para** no encontrarme campos descuadrados o desproporcionados.

**AC1 — Búsqueda de comunidades**

- **Given** que uso Firefox en escritorio
- **When** abro el buscador de comunidades
- **Then** los campos «Nombre», «Ciudad» y «Código postal» y el botón «Buscar» caben dentro de su panel

**AC2 — Campo de precio**

- **Given** que publico o edito un anuncio
- **When** veo el campo de precio
- **Then** tiene un ancho proporcionado a su contenido y el símbolo «€» aparece dentro del campo, alineado con el importe

### HU-30 Ver las fotografías de un anuncio a pantalla completa

**Como** vecino interesado en un anuncio, **quiero** ampliar sus fotografías y pasar de una a otra, **para** ver bien lo que se ofrece.

**AC1 — Ampliar**

- **Given** que estoy en el detalle de un anuncio con fotografías
- **When** pulso la imagen principal
- **Then** la veo a pantalla completa, en primer plano, con el número de imagen («2 / 3») y un botón para cerrar

**AC2 — Carrusel**

- **Given** que veo a pantalla completa un anuncio con varias fotografías
- **When** pulso las flechas laterales, uso las flechas del teclado o deslizo el dedo a izquierda o derecha
- **Then** paso a la imagen siguiente o anterior, de forma circular

**AC3 — Cerrar**

- **Given** que veo una fotografía a pantalla completa
- **When** pulso «Cerrar», la tecla Escape o el fondo fuera de la imagen
- **Then** vuelvo al detalle del anuncio, que muestra la última imagen que he visto

### HU-31 Acceder como administrador de plataforma a cualquier comunidad

**Como** administrador de plataforma, **quiero** entrar en cualquier comunidad sin tener que solicitar acceso, **para** poder supervisarla y publicar en ella.

**AC1 — Sin solicitar acceso**

- **Given** que soy administrador de plataforma
- **When** busco comunidades
- **Then** veo «Entrar» en todas ellas, aunque no sea miembro o mi solicitud esté pendiente, rechazada o bloqueada

**AC2 — Anuncios y gestión**

- **Given** que soy administrador de plataforma y no tengo una membresía aprobada en una comunidad
- **When** entro en ella
- **Then** veo sus anuncios, la búsqueda y los botones «Publicar anuncio» y «Gestionar comunidad»

**AC3 — Mis anuncios se ven**

- **Given** que soy administrador de plataforma sin membresía aprobada en una comunidad
- **When** publico un anuncio en ella
- **Then** aparece en el listado y en la búsqueda para todos sus miembros

### HU-32 Entender qué hace la moderación de un anuncio

**Como** administrador de comunidad, **quiero** que la acción de moderar un anuncio se llame «Ocultar», **para** distinguirla claramente de «Eliminar» y «Marcar como finalizado».

**AC1 — Ocultar**

- **Given** que gestiono una comunidad y abro un anuncio visible
- **When** veo sus acciones
- **Then** aparece «Ocultar anuncio» y, al pulsarlo, se me pide confirmar con «¿Ocultar este anuncio?» y el botón «Ocultar»

**AC2 — Textos coherentes**

- **Given** que se ha ocultado un anuncio
- **When** vuelvo al listado, lo abro como autor o gestor, o el autor intenta editarlo
- **Then** veo «Anuncio ocultado.», «Este anuncio está oculto y no se muestra en la comunidad.» o «Este anuncio ha sido ocultado por la administración de la comunidad.», y en ningún texto visible aparece «retirar»

---

## Épica 12 — Documentación técnica

La documentación técnica describe la arquitectura tal y como está implementada, para que quien mantiene o evalúa el proyecto no tenga que contrastarla con el código.

### HU-33 Ver dónde se aplica la seguridad en el diagrama de arquitectura

**Como** desarrollador, **quiero** que la documentación de arquitectura sitúe la autenticación JWT, la autorización por roles y CORS dentro de la API y describa las cabeceras de seguridad de la web como están implementadas, **para** entender dónde se aplica de verdad cada medida y no buscar componentes que no existen.

**AC1 — Seguridad dentro de FastAPI**

- **Given** que abro el diagrama de arquitectura del `readme.md` (§2.1)
- **When** sigo una petición del frontend al backend
- **Then** CORS, JWT Auth y RBAC aparecen dentro del bloque de FastAPI, en el orden en que se aplican y antes de la lógica de negocio, y no hay ninguna capa de seguridad entre el frontend y el backend

**AC2 — Descripción coherente**

- **Given** que leo la descripción de componentes (§2.2)
- **When** busco dónde se aplican la autenticación, los roles y CORS
- **Then** se describen como parte de la API y no como un componente independiente

**AC3 — Cabeceras de seguridad de la web**

- **Given** que leo la arquitectura (§2.1, §2.2) y la seguridad (§2.5) del `readme.md`
- **When** busco cómo protege la web sus respuestas
- **Then** veo que las cabeceras se configuran en Next.js (`next.config.ts`) y la `Content-Security-Policy` con un *nonce* por petición (`proxy.ts`), y Helmet no aparece como parte de la arquitectura

**AC4 — Diagrama válido**

- **Given** el diagrama actualizado
- **When** se renderiza en GitHub
- **Then** se muestra sin errores
