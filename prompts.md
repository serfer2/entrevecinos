> Detalla en esta sección los prompts principales utilizados durante la creación del proyecto, que justifiquen el uso de asistentes de código en todas las fases del ciclo de vida del desarrollo. Esperamos un máximo de 3 por sección, principalmente los de creación inicial o  los de corrección o adición de funcionalidades que consideres más relevantes.
Puedes añadir adicionalmente la conversación completa como link o archivo adjunto si así lo consideras


## Índice

- [0. Resumen del trabajo y herramientas utilizadas](#0-resumen-del-trabajo-y-herramientas-utilizadas)
  - [Herramientas](#herramientas)
  - [Modelos y tareas](#modelos-y-tareas)
  - [Skills, subagentes, rules y comandos](#skills-subagentes-rules-y-comandos)
  - [Prompts y workflows principales](#prompts-y-workflows-principales)
- [1. Descripción general del producto](#1-descripción-general-del-producto)
- [2. Arquitectura del Sistema](#2-arquitectura-del-sistema)
  - [**2.1. Diagrama de arquitectura:**](#21-diagrama-de-arquitectura)
  - [**2.2. Descripción de componentes principales:**](#22-descripción-de-componentes-principales)
  - [**2.3. Descripción de alto nivel del proyecto y estructura de ficheros**](#23-descripción-de-alto-nivel-del-proyecto-y-estructura-de-ficheros)
  - [**2.4. Infraestructura y despliegue**](#24-infraestructura-y-despliegue)
  - [**2.5. Seguridad**](#25-seguridad)
  - [**2.6. Tests**](#26-tests)
- [3. Modelo de Datos](#3-modelo-de-datos)
- [4. Especificación de la API](#4-especificación-de-la-api)
- [5. Historias de Usuario](#5-historias-de-usuario)
- [6. Tickets de Trabajo](#6-tickets-de-trabajo)
  - [6.1 Implementación de tickets de trabajo](#61-implementación-de-tickets-de-trabajo)
- [7. Pull Requests](#7-pull-requests)

---

## 0. Resumen del trabajo y herramientas utilizadas

### Herramientas

- **Codex:** documentación inicial del `readme.md`: definición del MVP, arquitectura, estructura del monorepositorio, infraestructura, seguridad, modelo de datos, primeros endpoints OpenAPI e historias de usuario.
- **Claude Code:** el asistente principal del resto del proyecto. Especificación completa de la API, historias de usuario, tickets y su refinamiento, implementación de todas las épicas (MVP, mejoras, validación del correo, experiencia de usuario, documentación técnica y producción en AWS), pruebas, *pull requests* y revisión de la documentación.
- **Cursor** y **ChatGPT** (como herramienta separada): no aparecen en el registro de trabajo.

### Modelos y tareas

- **GPT-5.6 Luna** (Codex): propósito y funcionalidades del producto.
- **GPT-6 Luna** (Codex): MVP, arquitectura, estructura del proyecto, infraestructura, seguridad, entidades, diagrama entidad-relación y primeros endpoints OpenAPI.
- **Claude Sonnet 5** (Claude Code): especificación completa de la API en varios ficheros, historias de usuario, selección de las tres principales y tickets de arranque.
- **Claude Opus 5.5** (Claude Code): tickets de todas las épicas y su refinamiento, implementación de TK-001 a TK-095, infraestructura de AWS con Terraform, CI/CD con GitHub Actions, verificación en producción, documentación y revisiones.

### Skills, subagentes, rules y comandos

- **OpenSpec** (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`): cada ticket se implementa como un cambio de OpenSpec con propuesta, diseño, especificaciones y tareas, que se archiva al terminar y actualiza `openspec/specs/`. Con «implementa TK-xxx», el agente encadena los tres pasos sin pedir confirmación entre ellos (regla guardada en la memoria del proyecto).
- **Skill `commit`** (propia): mensajes en Conventional Commits, en inglés y con el porqué en el cuerpo.
- **Caveman:** respuestas abreviadas del agente para ahorrar contexto.
- **Plugin de Playwright:** recorrido de extremo a extremo de la web en producción (registro, comunidad y anuncio con fotografías).
- **Subagentes:** el de lectura web, para consultar documentación de AWS (p. ej. los campos de los registros de CloudFront).
- **Rules del proyecto:**
  - `AGENTS.md`: comandos, arquitectura, convenciones y límites, enlazado desde `CLAUDE.md`, junto con la guía de AWS para la cuenta del proyecto;
  - `openspec/config.yaml`: contexto del proyecto y reglas para cada artefacto (p. ej. que los cambios de infraestructura actualicen `infra/aws/README.md`).
- **Herramientas de apoyo:** AWS CLI con sesión temporal (`aws login`), Terraform, Docker y `make` en contenedores. El servidor MCP de AWS no llegó a conectarse, así que se usó la AWS CLI.

### Prompts y workflows principales

`prompts.md` sigue las secciones del `readme.md`:

1. **Producto y MVP** (§1): propósito, valor, funcionalidades y alcance del MVP.
2. **Diseño de la solución** (§2): diagramas Mermaid de arquitectura e infraestructura, componentes, monorepositorio con arquitectura limpia y seguridad.
3. **Datos y API** (§3 y §4): entidades, diagrama ER y contrato OpenAPI multi-fichero.
4. **Planificación** (§5 y §6): historias de usuario con criterios Gherkin, tickets por épica y refinamiento; las inferencias se marcan con `(asumido)`.
5. **Implementación** (§6.1): un cambio de OpenSpec y un commit por ticket o por historia, con sus pruebas, siempre en contenedores.
6. **Producción** (§6 y §6.1): épica de AWS, refinamiento por coste y seguridad, e implementación ticket a ticket con verificación en producción (despliegue continuo, alarmas, ensayos de recuperación).
7. **Pruebas y entregas** (§2.6 y §7): verificación de extremo a extremo y *pull requests* de cada entrega.

---

## 1. Descripción general del producto

**Prompt 1**. Objetivos 

**Agente:** GPT-5.6 Luna - **Contexto:** El agente ya conoce la descripción general del proyecto

```
Explica el propósito del producto. Que valor aporta, qué soluciona, y para quién.
```

**Prompt 2**.  Características y funcionalidades principales 

**Agente:** GPT-5.6 Luna

```
Enumera y describe las características y funcionalidades específicas que tiene el producto
```

**Prompt 3**. MVP

**Agente:** GPT-6 Luna - **Contexto:** El agente ya conoce las funcionalidades descritas en la sección 1.2 del readme

```
Rol: Eres un product owner especialista en proyectos de tipo marketplace.
Objetivo: Dada la información contenida en el readme.md, particularmente la sección 1.2, describe las funcionalidades básicas que contendría el MVP del proyecto
```

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:** Diagrama de arquitectura

**Agente:** GPT-6 Luna 

```
Rol: eres un software architect con experiencia en el diseño de soluciones de software.
Objetivo: tienes que hacer un diagrama Mermaid con la arquitectura del sistema.
Requisitos:
- Capa de frontend con React + Next.js v16 + TypeScript y TailwindCSS.
- Capa de seguridad entre la capa de frontend y la de backend. Implementa JWT Auth, CORS y RBAC  Helmet.
- Capa de Backend dockerizado con Python y Fast API
- Capa de persistencia: Base de datos PostgreSQL 16, dockerizada y con volumen persistente. También almacenamiento para ficheros de imagen
Explica si sigue algún patrón predefinido, justifica por qué se ha elegido esta arquitectura, y destaca los beneficios principales que aportan al proyecto y justifican su uso, así como sacrificios o déficits que implica.
```

### **2.2. Descripción de componentes principales:**

**Prompt 1:**

**Agente:** GPT-6 Luna 
```
Describe los componentes más importantes, incluyendo la tecnología utilizada
```

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

**Prompt 1:** Estructura de carpetas

**Agente:** GPT-6 Luna - **Contexto:** El agente ya conoce la estructura del proyecto y los componentes principales

```
Rol: eres un software architect con experiencia en el diseño de soluciones de software.
Objetivo: Representa la estructura del proyecto y explica brevemente el propósito de las carpetas principales, así como si obedece a algún patrón o arquitectura específica.
Requisitos:
- Se trata de un mono-repositorio modular.
- Arquitectura limpia y buenas prácticas para cada uno de los componentes que forman el sistema.
```

### **2.4. Infraestructura y despliegue**

**Prompt 1:** Infraestructura

**Agente:** GPT-6 Luna

```
Crea un diagrama Mermaid y una explicación técnica que compare la infraestructura de desarrollo local (Docker Compose) versus la infraestructura cloud necesaria para la puesta en producción
```

### **2.5. Seguridad**

**Prompt 1:** Elementos de seguridad

**Agente:** GPT-6 Luna

```
Rol: eres un software architect con experiencia en el ámbito de la seguridad informática.
Contexto: revisa las secciones ya rellenas del fichero de readme.md. Con especial atención en la sección **2. Arquitectura del Sistema**
Objetivo: enumera y describe las principales prácticas de seguridad que incorpora el presente proyecto.
Añade ejemplos cuando sea pertinente y elabora tu respuesta en formato Markdown
```

### **2.6. Tests**

Las pruebas unitarias y de integración no tienen *prompts* propios: forman parte de cada ticket (regla de `openspec/config.yaml`: «Incluir las pruebas en la tarea que implementa el comportamiento») y el agente las ejecuta con `make ci-api` y `make ci-web` antes de dar el ticket por terminado. Los *prompts* de esta sección son los de verificación sobre producción.

**Prompt 1:** Recorrido de extremo a extremo con Playwright

**Agente:** Claude Code (Opus 5.5) - **Contexto:** CloudFront ya sirve la web (TK-087); falta comprobar el recorrido completo en producción

```
drive it with Playwright, I'll click the email link
```

**Nota**

El agente registra una cuenta en `https://entrevecinos.org`, espera a que se pulse el enlace de validación que llega por SES, crea una comunidad y publica un anuncio con dos fotografías, comprobando cada página y la consola del navegador.

**Prompt 2:** Permisos de la identidad de GitHub Actions

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Creados el usuario de CI y el rol de despliegue (TK-088)

```
run the test script
```

**Nota**

El script crea una clave temporal del usuario de CI, comprueba 12 casos permitidos y denegados (ECR, SSM, Parameter Store, IAM) y borra la clave al terminar.

**Prompt 3:** Ensayos de recuperación

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Implementado `restore.sh` (TK-092)

```
implement ticket 092
```

**Nota**

El agente prepara los guiones de ensayo y se ejecutan en producción: restauración de una copia en una base aparte, PostgreSQL sobre un volumen creado desde un *snapshot* y recuperación de una imagen borrada. El resultado queda registrado en `infra/aws/README.md`.

---

### 3. Modelo de Datos

**Prompt 1:** Entidades

**Agente:** GPT-6 Luna - **Contexto:** El agente conoce el diseño y la arquitectura propuesta 

```
Rol: eres un software engineer con experiencia en el diseño de modelos de datos.
Objetivo: elaborar un listado de entidades para el modelo de datos del proyecto.
Requisitos:
- Se específico en los campos que componen cada entidad: tipo, descripción, constraints, nullable?, enums ...
- Identiffica las claves primarias así como las foráneas.
- Identifica los índices, simples o compuestos, para que las consultas a la BD sean eficientes
```

**Prompt 2:** Diagrama ER

**Agente:** GPT-6 Luna - **Contexto:** El punto de partida es la lista de entidades resultante del prompt anterior

```
A partir de la respuesta anterior, elabora un diagrama entidad-relación con Mermaid. Utiliza todos los parámetros que permite la sintaxis para dar el máximo detalle.
```

---

### 4. Especificación de la API

**Prompt 1:** OpenAPI

**Agente:** GPT-6 Luna - **Contexto:** El agente conoce el diseño de los puntos anteriores. 

```
En el backend, para los endpoint del API, genera la especificación en formato OpenAPI. Ordena los endpoint por importancia (los más relevantes primero) y dame los tres primeros.
```

**Prompt 2:** Especificación completa multi-fichero

**Agente:** Claude Code (Sonnet 5) - **Contexto:** El agente conoce el README completo (MVP, modelo de datos y los 3 primeros endpoints)

```
Quiero completar la doc del API. Todos los endpoint necesarios para el proyecto deben quedar documentados. Crea los ficheros y/o carpetas que consi
deres necesarios de acuerdo con las buenas prácticas de OpenAPI
```

---

### 5. Historias de Usuario

**Prompt 1:** Creación de User Histories

**Agente:** Claude Code (Sonnet 5) - **Contexto:** El agente conoce el README completo, el MVP y ha completado las especificaciones del API

```
## Rol 

Tu rol es el de un senior product owner cuyo objetivo es crear user stories, bien acotadas y con criterios de aceptación claros

## Objetivo

Redacta las historias de usuario completas siguiendo las mejores prácticas para el desarrollo del MVP del presente proyecto siguiendo las buenas prácticas

## Formato

**Como** [rol], **quiero** [acción], **para** [beneficio].

## Acceptance criteria (AC)
Cada Story debe tener de 3 a 5 AC verificables siguiendo el formato Gherkin (**Given** / **When** / **Then**). Cada una de las 3 frases del Given/When/Then debe ir con salto de línea

## Agrupacion
Las stories agrupadas por módulo, caso de uso o épica, según tenga más sentido para EntreVecinos

## Restricciones
- Solo funcionalidades del MVP; sin inventar features que no estén ya documentadas en el readme.md.
- No hagas estimaciones de tiempos ni SP ni nada por el estilo.
- No hagas menciones ni propuestas que tengan que ver con la arquitectura técnica.

## Instrucción de transparencia
Debes marcar con `(asumido)`, todas las inferencias que hagas y que no estén explicitamente en el readme.md.
```

**Prompt 2:** Selección

**Agente:** Claude Code (Sonnet 5) - **Contexto:** El agente acabe de crear las UH y las ha agrupado por épica.

```
elige las 3 historias de usuario más relevantes y las copias al readme
```

---

### 6. Tickets de Trabajo

**Prompt 1:** 3 tickets de arranque

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Nos centramos en el arranque de la estructura técnica de desarrollo para el proyecto

```
Genera los siguientes tres tickets de desarrollo. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto.

- Ticket 1 - Infrastructura: Añade db a Docker Compose con PostgreSQL 16. Si no existe configuración de docker y/o docker compose, creala. La base de datos debe tener volumen persistente para salvar datos.
  
- Ticket 2 - Backend: Añade fastapi conforme a lo descrito en el proyecto, pero no implementes endpoints ni lógica de negocio. Sólo la estructura vacía. Añadelo también a docker y docker compose, con un volumen persistente para los assets.

- Ticket 3 - Frontend : Añade las configuraciones para el frontend, incluye lo necesario en docker y docker compose pero sin implementar todavía el código del frontend
```

**Prompt 2:** Dev Makefile

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Facilitamos las pruebas y el desarollo

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

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Facilitamos las pruebas y el desarollo

```
Los tickets de cada historia de usuario deben estar agrupados en carpetas con nombre "HU-xxx-<nombre-de-la-historia-de-usuario>" donde xxx es la secuencia o número de historia de usuario. Los 4 tickets existentes deben ser movidos a docs/product/tickets/00-infra/. Actualiza el README.
```

**Prompt 4:** Crear tickets para Épica 1 — Registro y perfil básico

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de infra están listos e implementados

```
Crea los tickets para `Épica 1 — Registro y perfil básico`. Un fichero por cada ticket. Siguiendo la estructura de carpetas: crea una carpeta para la épica en docs/product/tickets y una subcarpeta por cada historia de usuario, numeradas en el orden en que han sido definidas en user-stories.md
```

**Prompt 4.1:** Refinement tickets Épica 01

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de Épica 1 han sidpo creados, los refinamos

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

La IA crea los tíckets de las Epica 02 a Épica 06 (historias de usuario de la 04 a la 16). Es decir, el resto de tickets del MPV. Procedo a refinarlos.

**Prompt 5.1:** Refinement tickets Épicas 02 a 06

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Resto de tickets del MVP han sidpo creados, los refinamos

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

El agente crea le épica 07 y el ticket 047. La solución implementada se resume:

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

#### 6.1 Implementación de tickets de trabajo

**Prompt 1:** Implementar infra de desarrollo

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Tickets de infra están listos

```
Implement infra tickets TK-01..TK-04  
```

**Prompt 2:** Implementar tickets de Epica 1

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

---

### 7. Pull Requests

**Prompt 1:** 

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Completada la implementación de la primera versión funcional del MVP

```
Abre la PR hacia main
```

**Nota**

Al no tener el cliente de `gh`instalado con el token de seguridad configurado, Claude propone que la abra yo a mano. Me da el título y el contenido de la misma.

**Prompt 2:**

**Agente:** Claude Code (Opus 5.5) - **Contexto:** EL proyecto está listo para la 2a entrega 

```
Haz git push y prepara una PR. No hagas la PR (gh client y el token necesario no están instalados). Sólo dame el título y el body de la PR para que yo la abra en Github
```

**Prompt 3:**

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Épica 13 terminada (TK-091 a TK-095) en la rama de la tercera entrega

```
give me a PR description ready to copy in GH
```

**Nota**

El agente lista los commits pendientes de `main` y redacta título y descripción siguiendo la plantilla de *pull request* del repositorio, con el resultado de las comprobaciones y lo que ocurrirá al fusionar (despliegue continuo).
