# Prompts completos de los tickets de trabajo

Anexo de [`prompts.md`](../prompts.md) §6, que recoge solo los tres *prompts* más relevantes. Aquí están todos los utilizados para crear, refinar e implementar los tickets de [`docs/product/tickets/`](product/tickets/README.md), en orden cronológico.

## Índice

- [1. Creación y refinamiento de tickets](#1-creación-y-refinamiento-de-tickets)
- [2. Implementación de tickets de trabajo](#2-implementación-de-tickets-de-trabajo)

---

## 1. Creación y refinamiento de tickets

**Prompt 1:** 3 tickets de arranque

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Nos centramos en el arranque de la estructura técnica de desarrollo para el proyecto

```
Genera los siguientes tres tickets de desarrollo. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto.

- Ticket 1 - Infrastructura: Añade db a Docker Compose con PostgreSQL 16. Si no existe configuración de docker y/o docker compose, creala. La base de datos debe tener volumen persistente para salvar datos.
  
- Ticket 2 - Backend: Añade fastapi conforme a lo descrito en el proyecto, pero no implementes endpoints ni lógica de negocio. Sólo la estructura vacía. Añadelo también a docker y docker compose, con un volumen persistente para los assets.

- Ticket 3 - Frontend : Añade las configuraciones para el frontend, incluye lo necesario en docker y docker compose pero sin implementar todavía el código del frontend
```

**Prompt 2:** Dev Makefile

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Facilitamos las pruebas y el desarrollo

```
Genera un ticket de desarrollo. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto.
El ticklet es para crear un Makefile con comandos:
 - build-frontend: construye las imágenes de docker necesarias para lanzar el servidor de desarrollo del frontend.
 - build-backend: construye las imágenes de docker necesarias para lanzar el servidor de desarrollo del backend.
 - build: build-frontend y build-backend.
 - dev: genera las imágenes de frontend y backend necesarias y levanta los servidores de desarollo de frontend y backend.
 - clean: tumba los servidores dedesarrollo de frontendy backend y elimina las imágenes de docker creadas.
```

**Prompt 3:** Organización de tickets

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Facilitamos las pruebas y el desarrollo

```
Los tickets de cada historia de usuario deben estar agrupados en carpetas con nombre "HU-xxx-<nombre-de-la-historia-de-usuario>" donde xxx es la secuencia o número de historia de usuario. Los 4 tickets existentes deben ser movidos a docs/product/tickets/00-infra/. Actualiza el README.
```

**Prompt 4:** Crear tickets para Épica 1 — Registro y perfil básico

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de infra están listos e implementados

```
Crea los tickets para `Épica 1 — Registro y perfil básico`. Un fichero por cada ticket. Siguiendo la estructura de carpetas: crea una carpeta para la épica en docs/product/tickets y una subcarpeta por cada historia de usuario, numeradas en el orden en que han sido definidas en user-stories.md
```

**Prompt 4.1:** Refinement tickets Épica 01

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de Épica 1 han sido creados, los refinamos

```
- En Tk-05, el nombre de la tabla de usuarios será users.
- Renombra los ficheros de ticket siguiendo el siguiente patrón Tk-05 -> Tk-005
```

**Prompt 5:** Crear tickets para resto de épicas

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de épica 1 están listos.

```
Crea los tickets para el resto de épicas.
```

**NOTA**

La IA crea los tickets de las Épicas 02 a 06 (historias de usuario de la 04 a la 16). Es decir, el resto de tickets del MVP. Procedo a refinarlos.

**Prompt 5.1:** Refinement tickets Épicas 02 a 06

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Resto de tickets del MVP han sido creados, los refinamos

```
Esto es el refinement de los tickets creados para las épicas 02 a 06.
- TK-012: Los nombres de las tablas son en singular. La de `users` es una excepción por coincidir con una palabra reservada de PostgreSQL. Añade esta aclaración en el README, donde corresponda. Corrige el resto de tickets si es necesario.
- TK-013: Añade el Límite de `description` de comunidades a CommunityCreate.yaml.
- TK-017: Debe añadir **Campo `status` en el `403`:** extensión del contrato (`Error` solo tiene `detail`) en `docs/api`.
- TK-019: Añade Licencia y versiones de MinIO. Documéntalo si es necesario.
- TK-023: CSP, al servir imágenes desde `localhost:9000` (y S3 en producción), la futura `Content-Security-Policy` (TK-003 §8) debe permitir ese origen en `img-src`. Añade o modifica uno o varios tickets para ello.
- TK-030: búsqueda mínima con 2 caracteres. Inclúyelo en la doc.
- TK-040: los anuncios de los miembros bloqueados deben quedar ocultos al bloquear al miembro.
- TK-042: Transiciones de estado de los anuncios. Añade dentro del MVP, en una historia nueva (por ejemplo, HU-09b «Marcar mi anuncio como reservado o finalizado»):
   - Añádelo a la documentación como parte del MVP.
   - Un ticket de backend que amplíe TK-042 con active ↔ reserved, active | reserved → completed, y completed como estado final (asumido).
   - Un ticket de frontend con los botones «Marcar como reservado», «Quitar reserva» y «Marcar como finalizado» en el detalle, visibles solo para el autor.
```

**Prompt 5.2:** Refinement tickets Épicas 02 a 06

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets han sido refinados y documentación actualizada

```
Haz commit de los tickets y la documentación
```

**Prompt 6:** Mejora de usabilidad: redirect root to login or home

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Funcionalidades del MVP ya están implementadas. Faltan algunas mejoras básicas de usabilidad

```
- Crea una nueva épica para "mejora de funcionalidades del MVP"
- Cuando levanto el servicio con make dev, no encuentro forma alguna de interactuar con el servicio. Sólo una página en blanco con un H1 con el nombre del sitio. Crea una historia de usuario con los tickets necesarios para solucionarlo.
```

**NOTA**

El agente crea la épica 07 y el ticket 047. La solución implementada se resume:

```
Cambio: / ahora redirige según la sesión:
- con sesión válida, va a /inicio;
- sin sesión, o si la API falla, va a /iniciar-sesion. Es el mismo criterio que ya usa esa página.
```

**Prompt 7:** Mejora de usabilidad: redirect inicio a comunidades

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Funcionalidades del MVP ya están implementadas. Faltan algunas mejoras básicas de usabilidad

```
En la épica EP-07, crea las siguientes historias de usuario con sus corespondientes tickets:
- Si tras hacer login, el usuario no pertenece a ninguna comunidad, debe ser redirigido a la lista de comunidades existentes.
- Si tras hacer login, el usuario pertenece a una sola comunidad, debe ser redirigido a dicha comunidad.

Esto forma parte del MVP. Actualiza la documentación si es necesario.
Implementa las hisotrias de usuario/tickets y haz un commit por cada HU una vez que haya sido implementada.
```

**Prompt 8:** Mejora de gestión: creación de comunidades

**Agente:** Claude Code (Opus 5.5) - **Contexto:** MVP listo, pero detectamos fallos en la gestión de comunidades.

```
Crea una épica nueva para mejora de gestión de comunidades.
Para dicha épica, crea las siguientes historias de usuario con sus corespondientes tickets:
- Cuando un usuario crea una comunidad, esta no será activa hasta que un platform_admin la apruebe.
- Las comunidades creadas por un platform_admin son aprobadas (activas) automáticamente.
- Un usuario no puede pedir crear una nueva comunidad si ya tiene una comunidad pendiente se ser aprobada.

Esto forma parte del MVP. Actualiza la documentación si es necesario.
Implementa las hisotrias de usuario/tickets y haz un commit por cada HU una vez que haya sido implementada.
```

**Prompt 9:** Logout

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El MVP no incluía el log out

```
Crea una épica nueva para el "log out".
Para dicha épica, crea una historia de usuario con sus corespondientes tickets:
- Un usuario registrado y logeado puede hacer cierre de sesión (log out). Al cerrar sesión va al raíz del sitio. En cuanto a UI y usabilidad, añade el cierre de sesión donde más convenga, de acuerdo con las buenas prácticas del sector 

Esto forma parte del MVP. Actualiza la documentación si es necesario.
Implementa la hisotria de usuario y haz un solo commit que incluya los cambios en la documentación
```

**Prompt 10:** Validación del email

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El MVP no incluía la validación de la dirección de correo electrónico

```
Crea una épica nueva para "validación de email".
Para dicha épica, crea una o varias historias de usuario con sus corespondientes tickets para cumplir con las siguientes condiciones:
- Cuando un usuario se registra, tiene que validar su dirección de correo electrónico. Para ello, el sistema le envía un email con un enlace de validación. En lugar de activar la cuenta automáticamente, el usuario ve un aviso de que ha recibido un email de confirmación.
- Una cuenta de usuario con una dirección de email que no ha sido validada, no puede estar activa, salvo que sea platform_admin.
- Un intento de registro con una cuenta de email que está pendiente de validación, devolverá error y dará la opción a recibir de nuevo el mensaje de validación.
- Los mensajes de validación tienen una caducidad de 24 horas.
- Cuando un usuario visita el enlace de validación, la cuenta de usuario queda activa y es redirigido a la lista de comunidades, como ocurría antes de implementar la validación de email.

Esto forma parte del MVP. Crea uno o varios tickets para actualizar la documentación. No implementes los cambios, quiero revisar los tickets primero.
```

**Prompt 11:** Validación del email (refinement)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Los tickets para validación de correo electrónico han sido creados pero no refinados

```
Aplica este refinement para los siguientes tickets
- TK-056: también se debe actualizar el `.env` con las variables nuevas necesarias.

Implementa las historias de usuario y haz un commit por cada HU
```

**Prompt 12:** Fix de comportamiento de link de validación expirado

**Agente:** Claude Code (Opus 5.5) - **Contexto:** La validación de email funciona pero los links expirados dan falso OK

```
Si alguien abre un enlace antiguo que fue reemplazado por uno enviado nuevamente, y no tiene una sesión activa, verá el mensaje «Tu correo electrónico ya está validado. Inicia sesión», a pesar de que la cuenta sigue en estado pendiente. Es necesario corregir esto para que se muestre un mensaje de error adecuado.
Crea una historia de usuario con los tickets necesarios para ello e impleméntala.
```

**Prompt 13:** Look & Feel y mejoras de usabilidad

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Desarrollo del MVP completado. Fase de mejoras y depuración

```
Crea una épica con historias de usuario y tickets para los siguientes cambios:

Rediseña el look & feel de esta web de anuncios clasificados para que transmita una conexión clara con la naturaleza y resulte sencilla, limpia y fácil de usar.
Antes de hacer cambios, revisa la estructura del proyecto y localiza las tecnologías, páginas y componentes que ya existen. Conserva las funcionalidades actuales y céntrate en la presentación visual; reutiliza los componentes y estilos del proyecto siempre que tenga sentido.
Dirección visual
  - Usa una paleta inspirada en la naturaleza: verdes suaves, tonos tierra y fondos claros, con buen contraste para que el texto se lea bien.
  - Da prioridad a la sencillez: espacios amplios, jerarquía visual clara y pocos elementos decorativos.
  - Haz que los anuncios sean fáciles de explorar, con tarjetas ordenadas que destaquen imágenes, título y precio.
  - Mantén una navegación intuitiva y una búsqueda y unos filtros fáciles de encontrar y utilizar.
  - Elige tipografía legible y consistente, y utiliza iconos solo cuando ayuden a entender una acción.
  - Asegúrate de que el diseño se adapte bien a móviles, tabletas y escritorio.
  - Evita que el resultado parezca una plantilla genérica: adapta las decisiones visuales al contenido y a la identidad que ya tenga el proyecto.
Implementa los cambios en el código existente. Al terminar, resume qué archivos modificaste y qué decisiones visuales aplicaste.

Cuando voy al buscador de comunidades, como admin, me sigue saliendo el botón de "solicitar acceso". Como admin, el acceso debería ser por defecto a cualquier comunidad.

Acabo de publicar un anuncio en la comunidad "Barrio HU21" y no aparece. Se debe considerar al platform_admin como miembro, igual que ya hace require_member.

Las imágenes en la ficha del anuncio se ven pequeñas. Quiero que al hacer click en ellas, se vean en grande en primer plano y pueda hacer carrusel a izquierda o derecha pusando botones o arrastrando el dedo en dispositivo táctil.
```

**Prompt 14:** Aplicar sugerencias del Feedback de entrega 1

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El feedback de la 1a entrega muestra deficiencias en la doc.

```
Crea una HU y los tickets y la implementación en openspec para llevar a cabo el siguiente cambio:
En la doc, el diagrama dibuja una capa de seguridad entre el frontend y el backend, pero JWT, roles y CORS viven dentro de la API; dibújalos dentro de FastAPI.
No lo implementes aún, quiero revisar los tickets
```

**Prompt 15:** Ajustar las definiciones de la doc del API

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El feedback de la 1a entrega muestra deficiencias en la doc del API y en el alcance del MVP

```
 Añade a la épica 12 historias de usuario y tickets para estos cambios:

  comprueba si el número de entidades del modelo de datos, coincide con las rutas definidas en docs/api. Si hay más rutas en la doc del api, esas rutas no pertenecen al MVP. Marca en la doc del api y en el resto de la doc, qué subconjunto es el del MVP y cuales están pendientes de implementar en futuras versiones. Asegúrate de que el README apunta a docs/api/openapi.yaml
  como la fuente de verdad y de que el fragmento incluido en él coincide.
```

**Prompt 16:** Creación de las tareas para puesta en producción en AWS

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El proyecto está listo para poner en producción. Es necesario preparar la infra en AWS

```
Eres un experto en infrastructura y AWS. Crea una nueva épica para crear todos los recursos necesarios en AWS para poner el proyecto en producción. La épica debe contener los tickets, siguiendo el orden necesario. No los implementes, quiero revisarlos y refinarlos antes de la implementación.
NOTAS:
- El dominio es "entrevecinos.org" y está configurado en Dinahosting
- Añade un límite de gasto mensual en AWS de 40 euros al mes
```

**Prompt 17:** Refinement de tickets de la épica 13 - reducción de costes

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Los tickets y las historias de usuario de la épica 13 han sido creados y es necesario refinarlos/corregirlos y tomar decisiones que han quedado abiertas 

```
Vamos a intentar recortar costes: De momento no es necesario alta disponibilidad, no nos preocupamos por eso hasta que el proyecto sea maduro y tenga mucho tráfico. Teninendo esto en cuenta, refactoriza la infrastructura y refleja los cambios en la documentación. Si tienes dudas pregúntame
```

**Prompt 18:** Refinement de tickets de la épica 13 - seguridad (secretos)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Los tickets y las historias de usuario de la épica 13 han sido creados y es necesario refinarlos/corregirlos y tomar decisiones que han quedado abiertas 

```
De acuerdo con el ticket 086, se pretende almacenar las los secretos en en fichero .env dentro de la propia instancia. Evítalo usando la alternativa mencionada: pasarlos solo por entorno al proceso de Compose. Documenta el cambio y dime cuales tickets se modifican.
```

**Prompt 19:** Refinement de tickets de la épica 13 - Documentación al día

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Los tickets y las historias de usuario de la épica 13 han sido creados y es necesario refinarlos/corregirlos y tomar decisiones que han quedado abiertas 

```
Con respecto a lo mencionado en el ticket 093, hay dos acciones que deben llevarse a cabo (crea la historia de usuario y/o tickets necesarios):
- Asegúrate de añadir una regla en openspec/config.yaml y en AGENTS.md para asegurarte de que infra/aws/README.md refleje cualquier cambio en la infrastructura.
- Inicialmente el README hablaba de contenedores gestionados y balanceador pero de momento la arquitectura va a ser distinta a la prevista. Asegúrate de que se documenta la decisión (coste, mientras el proyecto no escale) y la evolución recomendada cuando sea maduro y tenga mucho tráfico: RDS (y después Multi-AZ), ECS Fargate + ALB, WAF propio, DNSSEC en Route 53, origen cifrado y orígenes VPC de CloudFront.
```

**Prompt 20:** Correo en producción: SES sigue en *sandbox*

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Épica 13 terminada, pero SES no sale del *sandbox* y solo entrega a direcciones verificadas: los vecinos no pueden validar su cuenta

```
con respecto al Tema operativo: SES sigue en sandbox... vamos a solucionarlo. Quiero que todo funcione en producción. Crea una historia de usuario/tickets en la épica 13 para abordar el problema
```

```
vamos a optar por un proveedor de SMTP alternativo. Explora los diferentes servicios y, con el coste como criterio fundamental y la facilidad de integración como segundo criterio, dame una lista de los 3 mejores
```

```
vamos con Brevo, actualiza TK-096 y TK-098
```

**Nota**

El agente crea la HU-40 con los tickets TK-096 a TK-098 y compara proveedores por coste y facilidad de integración. Con Brevo elegido, los tickets pasan a cubrir el alta manual en Brevo (TK-096), el aviso de los fallos de envío (TK-097) y la integración por SMTP con sus registros DNS en Terraform (TK-098). SES queda configurado como vuelta atrás.

**Prompt 21:** Cupo de correos por coste

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El plan gratuito de Brevo tiene un límite y el gasto mensual no debe pasar de 40 €

```
añade un ticket para asegurarse de que no se envían más de 5000 emails al mes. Si esto ocurre, bloquea el envío de email. El cálculo es del 06 del mes en curso al 06 del mes siguiente
```

```
el límite debe quedar documentado explicando que se debe a una restricción por costes
```

**Nota**

El agente crea TK-099: la tabla `email_quota`, una reserva atómica antes de cada correo, un `503` cuando no queda cupo y alarmas al 80 % y al llegar al límite.

**Prompt 22:** Recuperación de la contraseña olvidada

**Agente:** Claude Code (Opus 5.5) - **Contexto:** La pantalla de inicio de sesión no ofrece ninguna salida a quien olvida su contraseña

```
En la pantalla de login, no hay enlace de "he olvidado mi contraseña", es necesario tenerlo. Crea una épica con sus historias de usuario y tickets para hacerlo. También debe quedar documentado como funcionalidad del MVP
```

**Nota**

El agente crea la Épica 14 con la HU-41 (pedir el enlace) y la HU-42 (elegir una contraseña nueva) y los tickets TK-100 a TK-105, de base de datos, backend, frontend y documentación.

**Prompt 23:** Avisos por correo de las solicitudes de acceso

**Agente:** Claude Code (Opus 5.5) - **Contexto:** En producción, una solicitud de acceso a una comunidad queda pendiente sin que la administración se entere

```
En producción, he hecho una solicitud de admisión para el usuario <vecino> pero nada ha ocurrido, <administrador> no se ha enterado. No hay correo de solicitud para aprobar la membresía ni nada por el estilo
```

```
crea una historia y tickets para el aviso por correo
```

```
El solicitante debe recibir aviso por correo cuando sea aceptado
```

**Nota**

Las direcciones de correo del primer *prompt* se han sustituido por `<vecino>` y `<administrador>`. El agente crea la HU-43 (aviso a la administración de la comunidad) y la HU-44 (aviso al vecino aprobado), con los tickets TK-106 a TK-108.

---

## 2. Implementación de tickets de trabajo

**Prompt 1:** Implementar infra de desarrollo

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de infra están listos

```
Implement infra tickets TK-01..TK-04  
```

**Prompt 2:** Implementar tickets de Épica 1

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de Épica 1 están listos

```
Los tickets de la Épica1 ya están revisados, impleméntalos
```

**NOTA**

Claude propone ir creando las specs en openspec a partir de los ficheros de tickets que hay en la carpeta `docs/product/tickets/00-infra`.

**Prompt 3:** Implementar los tickets de las Épicas 02 a 06 y los tickets adicionales

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Todos los tickets del MVP han sido generados, revisados y refinados

```
Implementa los tickets que falten por implementar. Revisa los que ya han sido implementados y asegúrate de que todos queden hechos
```

**Prompt 4:** Implementar los tickets de la Épica de mejoras y depurado de experiencia de usuario

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Todos los tickets de la épica 11 están listos para implementar.

```
Implementa los tickets de la épica 11
```

**Prompt 5:** Implementar los tickets de la Épica 12

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Todos los tickets de la épica 12 han sido revisados y refinados y están listos para implementar.

```
Implementa los tickets de la épica 12
```

**Prompt 6:** Implementar los tickets de la Épica 13 (producción en AWS)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de la épica 13 refinados. Se implementan uno a uno, en orden, porque cada uno se aplica en AWS y se verifica en producción antes del siguiente

```
let's start with 087. Tell me if I've to do any manual step and/or configuration
```

```
implementa TK-087
```

**Nota**

El mismo *prompt* («implementa TK-0xx») se usa de TK-078 a TK-095. El agente encadena propuesta, implementación y archivo de OpenSpec, se detiene cuando hace falta una decisión o un paso manual y la persona aplica Terraform y confirma los correos. Las decisiones que se apartan de los tickets se tomaron así, con alternativas y coste: sin WAF ni OIDC porque la política del plan FREE de AWS los deniega, o la alarma de errores de la web medida en el proxy porque SNS no está permitido en `us-east-1`.

**Prompt 7:** Revisión de la documentación

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Épica 13 terminada; antes de la entrega se revisa toda la documentación

```
Eres un gestor de proyectos experimentado. Revisa minuciosamente TODA la documentación del proyecto, incluyendo prompts.md. Quiero que me digas si hay partes por completar, desactualizadas o si falta algún aspecto importante que no se haya cubierto
```

```
prepara los puntos 2 a 5
```

**Prompt 8:** Correo de producción con Brevo y cupo (TK-096 a TK-099)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Alta en Brevo hecha a mano (TK-096); los registros DNS de Brevo y la IP elástica autorizada los crea Terraform (TK-098)

```
implementa TK-099
```

```
el correo ha rebotado. Haz tus comprobaciones y borra la cuenta al terminar. Sigue con el ticket, haz commit y push
```

**Nota**

La entrega se comprueba en producción: correos recibidos en Gmail y Outlook con DKIM y DMARC en `pass`. En TK-097 el agente fuerza la alarma de fallos de envío para comprobar que llegan los avisos. Después se registra una cuenta con una dirección inexistente: el rebote aparece en Brevo, pero no cuenta como fallo de envío de la API. El agente lo comprueba y borra la cuenta de prueba.

**Prompt 9:** Recuperación de la contraseña (Épica 14)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets TK-100 a TK-105 creados y revisados

```
implementa TK-100
```

```
acepto el riesgo, haz commit y push
```

**Nota**

Se implementa un ticket por *prompt*, de TK-100 a TK-105, con un commit cada uno. El segundo *prompt* acepta un riesgo que el agente señala al cerrar TK-105: el seguimiento de clics de Brevo, que no se puede desactivar en el correo transaccional, también reescribe el enlace para restablecer la contraseña, igual que ya hacía con el de validación. Tras desplegar, el recorrido completo se prueba en producción: pedir el enlace, cambiar la contraseña y recibir el aviso del cambio.

**Prompt 10:** Avisos de las solicitudes de acceso (TK-106 a TK-108)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de la HU-43 y la HU-44 creados

```
implementa TK-106
```

```
implementa TK-108
```

```
implementa TK-107
```

**Prompt 11:** Corrección del aviso al solicitar acceso

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Avisos desplegados (TK-106 a TK-108); al probarlos en producción, la web no confirma la solicitud

```
cuando un usuario hace click en "Solicitar acceso", no aparece mensaje alguno. El botón desaparece y vuelve a aparecer instantáneamente. Pero la solicitud de acceso llega al admin. Si vielvo a hacer click en el botón o refresco la página, se queda en "solicitud pendiente"
```

**Nota**

La API enviaba los correos en segundo plano antes de confirmar la transacción. La corrección confirma primero la transacción y después envía los correos. Se comprueba en producción: el aviso aparece y los correos llegan.
