# Historias de usuario del MVP — EntreVecinos

Historias del MVP definido en la sección 1.2 del `readme.md`. Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## Roles

- **Visitante**: persona sin cuenta.
- **Vecino**: usuario registrado con sesión iniciada.
- **Miembro**: vecino con acceso aprobado a una comunidad.
- **Administrador de comunidad**: persona que gestiona los miembros y los anuncios de su comunidad.

## Fuera de alcance

No se incluyen funcionalidades posteriores al MVP: perfil profesional, notificaciones automáticas, sistema completo de denuncias, panel avanzado de administración y mensajería interna. Tampoco la recuperación de contraseña ni el cierre de sesión, que no aparecen en el README.

## Índice

| Épica | Historias |
|---|---|
| 1. Registro y perfil básico | HU-01, HU-02, HU-03 |
| 2. Comunidades | HU-04, HU-05, HU-06 |
| 3. Gestión de anuncios | HU-07, HU-08, HU-09, HU-09b |
| 4. Explorar y encontrar anuncios | HU-10, HU-11, HU-12, HU-13 |
| 5. Detalle y contacto | HU-14, HU-15 |
| 6. Administración mínima | HU-16, HU-17 |
| 7. Mejora de funcionalidades del MVP | HU-18 |

---

## Épica 1 — Registro y perfil básico

### HU-01 Registrarme con mi correo electrónico

**Como** visitante, **quiero** crear una cuenta con mi correo electrónico y una contraseña, **para** poder usar EntreVecinos.

**AC1 — Registro correcto**

- **Given** que no tengo cuenta y estoy en el formulario de registro
- **When** introduzco mi nombre, un correo válido no registrado y una contraseña válida y envío el formulario
- **Then** se crea mi cuenta y accedo a la aplicación con la sesión iniciada (asumido)

**AC2 — Correo ya registrado**

- **Given** que ya existe una cuenta con el correo `vecino@example.com`
- **When** intento registrarme con ese mismo correo
- **Then** veo un mensaje que indica que el correo ya está en uso y no se crea ninguna cuenta

**AC3 — Datos inválidos**

- **Given** que estoy en el formulario de registro
- **When** envío el formulario con el correo mal formado, el nombre vacío o una contraseña que no cumple los requisitos (asumido)
- **Then** veo un mensaje de error junto a cada campo incorrecto y no se crea la cuenta

### HU-02 Iniciar sesión

**Como** vecino registrado, **quiero** iniciar sesión con mi correo y contraseña, **para** acceder a mi comunidad y a mis anuncios.

**AC1 — Acceso correcto**

- **Given** que tengo una cuenta
- **When** introduzco mi correo y mi contraseña correctos
- **Then** accedo a la aplicación con mi sesión iniciada

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

- **Given** que he creado una comunidad
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
