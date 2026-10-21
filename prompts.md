> Detalla en esta sección los prompts principales utilizados durante la creación del proyecto, que justifiquen el uso de asistentes de código en todas las fases del ciclo de vida del desarrollo. Esperamos un máximo de 3 por sección, principalmente los de creación inicial o  los de corrección o adición de funcionalidades que consideres más relevantes.
Puedes añadir adicionalmente la conversación completa como link o archivo adjunto si así lo consideras


## Índice

- [0. Resumen del trabajo y herramientas utilizadas](#resumen-del-trabajo-y-herramientas-utilizadas)
- [1. Herramientas](#1-herramientas)
- [2. Modelos y tareas](#2-modelos-y-tareas)
- [3. Skills, subagentes, rules y comandos](#3-skills-subagentes-rules-y-comandos)
- [4. Prompts y workflows principales](#4-prompts-y-workflows-principales)
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
- [7. Pull Requests](#7-pull-requests)

---

## 0. Resumen del trabajo y herramientas utilizadas

### Herramientas

- **Codex:** se utilizó para revisar y completar la documentación del proyecto en `readme.md`: definición del MVP, arquitectura, estructura del monorepositorio, infraestructura, seguridad, modelo de datos, especificación OpenAPI y user stories.
- **Claude Code:** según `prompts.md`, se utilizó para completar la especificación amplia de la API, redactar historias de usuario y preparar tickets de arranque.
- **Cursor:** no aparece documentado en `prompts.md`.
- **ChatGPT:** no aparece como herramienta separada en el registro; las interacciones documentadas con GPT se atribuyen a Codex.

### Modelos y tareas

Según `prompts.md`:

- **GPT-5.6 Luna:** descripción del propósito y las funcionalidades del producto.
- **GPT-6 Luna:** definición del MVP y elaboración de los apartados de arquitectura, estructura del proyecto, infraestructura, seguridad, entidades del modelo de datos, diagrama entidad-relación y primeros endpoints OpenAPI.
- **Claude Code (Sonnet 5):** especificación completa de la API en varios ficheros, historias de usuario y selección de las tres historias más relevantes, además de tickets iniciales para infraestructura, backend y frontend.

En esta conversación, Codex ayudó a desarrollar y revisar esos contenidos y actualizó referencias de tablas en el punto 3.2 para mantener los nombres de entidades en singular.

### Skills, subagentes, rules y comandos

- **Skills de Claude:** el usuario indica que utilizó **Caveman** y **OpenSpec**.
- **Skills de Codex:** no se aplicó ninguna skill específica durante este trabajo.
- **Subagentes:** no se utilizaron.
- **Rules y comandos personalizados:** `prompts.md` no documenta reglas ni comandos personalizados utilizados.
- **Instrucciones del proyecto:** `AGENTS.md` hacía referencia a `RTK.md`, pero esos archivos no estaban disponibles en la carpeta cuando se revisaron.

### Prompts y workflows principales

`prompts.md` organiza el trabajo siguiendo las secciones del README y registra los prompts empleados en distintas fases:

1. **Definición del producto y del MVP:** prompts para explicar el propósito, valor y funcionalidades de EntreVecinos y, a partir de estas, acotar las capacidades básicas del MVP.
2. **Diseño de la solución:** prompts para crear diagramas Mermaid de arquitectura e infraestructura, describir componentes, proponer la estructura de un monorepositorio modular con arquitectura limpia y documentar prácticas de seguridad.
3. **Datos y API:** prompts para listar entidades, campos, tipos, constraints e índices; generar el diagrama ER; y especificar en OpenAPI los endpoints prioritarios. Claude Code recibió después la tarea de completar la especificación de la API en varios ficheros.
4. **Planificación del producto y desarrollo:** prompts para redactar user stories del MVP con criterios Gherkin y marcar inferencias con `(asumido)`, seleccionar historias prioritarias y preparar tickets iniciales para PostgreSQL en Docker Compose, la estructura del backend FastAPI y la configuración del frontend.

Los apartados de tests y pull requests de `prompts.md` siguen vacíos. En el README, la sección de tests también figura como pendiente.

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

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**

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

**Prompt 5.1:** Refinement tickets Épicas 02 a 06

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

**Prompt 9:** Validación del email

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

**Prompt 10:** Validación del email (refinement)

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Los tickets para validación de correo electrónico han sido creados pero no refinados

```
Aplica este refinement para los siguientes tickets
- TK-056: también se debe actualizar el `.env` con las variables nuevas necesarias.

Implementa las historias de usuario y haz un commit por cada HU
```

**Prompt 11:** Fix de comportamiento de link de validación expirado

**Agente:** Claude Code (Opus 5.5) - **Contexto:** La validación de email funciona pero los links expirados dan falso OK

```
Si alguien abre un enlace antiguo que fue reemplazado por uno enviado nuevamente, y no tiene una sesión activa, verá el mensaje «Tu correo electrónico ya está validado. Inicia sesión», a pesar de que la cuenta sigue en estado pendiente. Es necesario corregir esto para que se muestre un mensaje de error adecuado.
Crea una historia de usuario con los tickets necesarios para ello
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

##### Importante

En esta fase, se implementan los tickets de las 6 primeras épicas (hasta el Tk-049). Las épicas posteriores, junto con sus historias de usuario y tickets, se han ido implementando a la vez que se iban creando y refinando.

---

### 7. Pull Requests

**Prompt 1:** 

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Completada la implementación de la primera versión funcional del MVP

```
Abre la PR hacia main
```

**Nota**

Al no tener el cliente de `gh`instalado con el token de seguridad configurado, Claude propone que la abra yo a mano en el siguiente contenido.

#### Título

```
feat: implementar el MVP de EntreVecinos (TK-001 a TK-046)
```

#### Contenido

~~~markdown
## Resumen

Implementación completa del MVP de EntreVecinos: los 46 tickets de `docs/product/tickets/` (infraestructura y épicas 1 a 6, incluida HU-09b). Cada ticket tiene su cambio de OpenSpec archivado en `openspec/changes/archive/` y un commit propio.

### Infraestructura
- PostgreSQL 16, API FastAPI y web Next.js 16 en Docker Compose, con `Makefile` (TK-001…TK-004).
- Almacenamiento de imágenes en MinIO con bucket privado y usuario de mínimos privilegios (TK-019). Usa la compilación comunitaria `pgsty/minio` con versión fija (AGPLv3), porque las imágenes oficiales ya no están en Docker Hub.
- Content-Security-Policy con nonce por petición (TK-046).
- `GET /v1/health`, usado por el healthcheck de la API.

### Funcionalidad
- **Épica 1:** registro, inicio de sesión (JWT en cookie `httpOnly`) y perfil.
- **Épica 2:** crear y buscar comunidades, solicitar el acceso y revisar las solicitudes; política única de permisos `CommunityAccess`.
- **Épica 3:** publicar anuncios con hasta 10 fotos (URL prefirmadas servidas por `/media/<id>`), editar, eliminar, y reservar o finalizar (HU-09b).
- **Épica 4:** listado paginado, búsqueda de texto completo en español sin tildes, filtros por tipo y categoría, orden por fecha o precio y selector de comunidad.
- **Épica 5:** detalle con galería y contacto con el anunciante (teléfono y correo, solo para miembros aprobados).
- **Épica 6:** bloquear, desbloquear y expulsar miembros (los anuncios del bloqueado se ocultan), y retirar o restaurar anuncios.

### Cambios de contrato (`docs/api`, compatibles)
- `CommunityCreate`/`CommunityUpdate.description` (2000) y `ListingCreate`/`ListingUpdate.description` (5000).
- `EUR` por defecto cuando hay precio sin moneda.
- `q` de la búsqueda con un mínimo de 2 caracteres.
- `MembershipError` y las respuestas `MembershipForbidden` (403) y `MembershipConflict` (409).
- `ListingOwner.email` obligatorio.
- Transiciones de estado del autor, con 409 para las no permitidas.

### Migraciones
`0001` users · `0002` community · `0003` unaccent · `0004` category/listing/media · `0005` búsqueda · `0006` auditoría de retirada.

## Cómo probar

```bash
cp .env.example .env      # un .env existente necesita las variables de «Almacenamiento»
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm api pytest
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

Resultado: 392 pruebas de API (más `ruff` y `alembic check`) y 293 de web, todas en verde; el build de producción compila.

## Notas
- **BREAKING (entorno local):** desaparecen el volumen `api_assets` y `ASSETS_DIR`. El volumen antiguo se puede borrar con `docker volume rm entrevecinos_api_assets`.
- El servicio `api` monta `docs/api` en solo lectura para la prueba que compara el esquema con el contrato.
- Operaciones del contrato marcadas como MVP pero sin historia ni ticket, y no implementadas: `POST`/`PATCH /categories`, `PATCH /communities/{id}`, `DELETE /media/{id}`, `GET /users/me/listings`, `DELETE /users/me` y el cambio de rol de un miembro.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
~~~

**Prompt 2:**

**Agente:** Claude Code (Opus 5.5) - **Contexto:** EL proyecto está listo para la 2a entrega 

```
Haz git push y prepara una PR. No hagas la PR (gh client y el token necesario no están instalados). Sólo dame el título y el body de la PR para que yo la abra en Github
```

**Nota**

El agente genera el siguiente contenido:

#### Título

```
feat: mejoras del MVP, aprobación de comunidades, cierre de sesión y validación del correo
```

#### Contenido

~~~markdown
## Resumen

Segunda tanda de funcionalidad sobre el MVP: épicas 7 a 10 (TK-047 a TK-062) y los tickets de la HU-27, pendientes de implementar. Cada ticket tiene su cambio de OpenSpec archivado en `openspec/changes/archive/` y las especificaciones de `openspec/specs/` están sincronizadas.                                                                                ### Épica 7 — Mejoras del MVP- `/` redirige a `/inicio` con sesión y a `/iniciar-sesion` sin ella (TK-047).  - Tras el registro o el inicio de sesión: sin comunidades → lista de comunidades; con una sola → esacomunidad (TK-048, TK-049).                                                     ### Épica 8 — Gestión de comunidades                                            - Las comunidades nuevas quedan pendientes hasta que un `platform_admin` las aprueba desde`/admin/comunidades` (TK-050, TK-051).                                          - Las que crea un `platform_admin` quedan activas al momento (TK-052).- Una sola comunidad pendiente por usuario: `409` y aviso en la web (TK-053, TK-### Épica 9 — Cierre de sesión                                                  - Botón «Cerrar sesión» en la cabecera privada (*Server Action* por `POST`, borra la *cookie* y va a`/`) (TK-055).                                                                  ### Épica 10 — Validación del correo                                            - **Mailpit** en Docker Compose como buzón de desarrollo (`http://localhost:8025`) y envío por SMTPdesde la API (TK-056).                                                          - El registro crea la cuenta **inactiva** y envía un enlace válido 24 horas; abrirlo activa la cuenta,inicia la sesión y lleva a `/comunidades`. Sin validar no se puede iniciar sesión (`403 email_not_verified`), salvo un `platform_admin`. Una restricción de la base de datos garantiza la regla (TK-057, TK-058, TK-060).
- Reenvío del correo de validación desde el registro, el enlace caducado y el inicio de sesión. Siempre responde `202`, para no revelar qué correos existen, y como mucho envía un correo por minuto (TK-059, TK-061).
- Documentación actualizada: `readme.md`, historias, `infra/`, `apps/api` y `apps/web` (TK-062).
- `/verificar-correo/error` enlaza siempre con la raíz.

### HU-27 (solo tickets)
TK-063 a TK-065 corrigen el mensaje «Tu correo ya está validado» que aparece al abrir un enlace
sustituido por un reenvío cuando la cuenta sigue pendiente. Están documentados y **pendientes de
implementar**.

### Cambios de contrato (`docs/api`)
- **Incompatible:** `registerUser` responde `RegistrationResponse` (`email`, `verification_expires_at`) en lugar de un JWT (TK-058).
- Nuevos `verifyEmail` (`POST /auth/email-verification`) y `resendEmailVerification` (`POST /auth/email-verification/resend`) (TK-058, TK-059).
- `loginUser`: `403` con `code: email_not_verified` (TK-058).
- `registerUser`: el `409` lleva `code` `email_in_use` o `email_pending_verification` (TK-059).
- `createCommunity` crea la comunidad pendiente de aprobación (salvo un `platform_admin`) y responde `409` si el usuario ya tiene una pendiente (TK-050, TK-052, TK-053).
- `adminListCommunities` y `adminUpdateCommunity` pasan al MVP (TK-050).

### Migraciones
`0007` una comunidad pendiente por usuario · `0008` validación del correo (`users.email_verified_at`, `ck_users_active_requires_verified_email`, tabla `email_verification`). Las cuentas existentes se dan por validadas.

## Cómo probar

```bash
# Un .env existente necesita las variables de «Correo (SMTP)» de .env.example
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

1. Regístrate en http://localhost:3000/registro y abre el correo en http://localhost:8025. El enlace te lleva a `/comunidades` con la sesión iniciada.
2. Con otra cuenta sin validar, inicia sesión: verás el aviso y el botón de reenvío.

Resultado: 461 pruebas de API (más `ruff`, `alembic check` y `redocly lint`) y 339 de web, todas en verde. El flujo de validación y reenvío está comprobado de extremo a extremo con Mailpit.

## Notas
- **BREAKING (entorno):** los `.env` existentes necesitan `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS`, `MAIL_FROM`, `WEB_PUBLIC_URL`, `EMAIL_VERIFICATION_TTL_HOURS` y `MAIL_UI_HOST_PORT`. Sin ellas, la API no arranca. Comprobación: `diff <(grep -o '^[A-Z_]*=' .env.example | sort) <(grep -o '^[A-Z_]*=' .env | sort)`.
- En producción, `SMTP_STARTTLS=true` y `WEB_PUBLIC_URL` con `https` son obligatorios (validados en `Settings`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
~~~

**Prompt 3:**
