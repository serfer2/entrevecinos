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
- [7. Pull Requests](#7-pull-requests)

---

## 0. Resumen del trabajo y herramientas utilizadas

### Herramientas

- **Codex:** documentación inicial del `readme.md`: definición del MVP, arquitectura, estructura del monorepositorio, infraestructura, seguridad, modelo de datos, primeros endpoints OpenAPI e historias de usuario.
- **Claude Code:** el asistente principal del resto del proyecto. Especificación completa de la API, historias de usuario, tickets y su refinamiento, implementación de todas las épicas (MVP, mejoras, validación del correo, experiencia de usuario, documentación técnica, producción en AWS, correo con Brevo, recuperación de la contraseña y avisos por correo), pruebas, *pull requests* y revisión de la documentación.

### Modelos y tareas

- **GPT-5.6 Luna** (Codex): propósito y funcionalidades del producto.
- **GPT-6 Luna** (Codex): MVP, arquitectura, estructura del proyecto, infraestructura, seguridad, entidades, diagrama entidad-relación y primeros endpoints OpenAPI.
- **Claude Sonnet 5** (Claude Code): especificación completa de la API en varios ficheros, historias de usuario, selección de las tres principales y tickets de arranque.
- **Claude Opus 5.5** (Claude Code): tickets de todas las épicas y su refinamiento, implementación de TK-001 a TK-108, infraestructura de AWS con Terraform, correo de producción con Brevo, CI/CD con GitHub Actions, verificación en producción, documentación y revisiones.

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

`prompts.md` sigue las secciones del `readme.md`, con un máximo de tres *prompts* por sección; los demás de §6 están en [`docs/prompts-completos.md`](docs/prompts-completos.md):

1. **Producto y MVP** (§1): propósito, valor, funcionalidades y alcance del MVP.
2. **Diseño de la solución** (§2): diagramas Mermaid de arquitectura e infraestructura, componentes, monorepositorio con arquitectura limpia y seguridad.
3. **Datos y API** (§3 y §4): entidades, diagrama ER y contrato OpenAPI multi-fichero.
4. **Planificación** (§5 y §6): historias de usuario con criterios Gherkin, tickets por épica y refinamiento; las inferencias se marcan con `(asumido)`.
5. **Implementación** (§6 y anexo): un cambio de OpenSpec y un commit por ticket o por historia, con sus pruebas, siempre en contenedores.
6. **Producción** (§6 y anexo): épica de AWS, refinamiento por coste y seguridad, e implementación ticket a ticket con verificación en producción (despliegue continuo, alarmas, ensayos de recuperación).
7. **Pruebas y entregas** (§2.6 y §7): verificación de extremo a extremo y *pull requests* de cada entrega.

---

## 1. Descripción general del producto

**Prompt 1:** Objetivos

**Agente:** GPT-5.6 Luna - **Contexto:** El agente ya conoce la descripción general del proyecto

```
Explica el propósito del producto. Que valor aporta, qué soluciona, y para quién.
```

**Prompt 2:** Características y funcionalidades principales

**Agente:** GPT-5.6 Luna

```
Enumera y describe las características y funcionalidades específicas que tiene el producto
```

**Prompt 3:** MVP

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

**Prompt 1:** Componentes principales

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
Quiero completar la doc del API. Todos los endpoint necesarios para el proyecto deben quedar documentados. Crea los ficheros y/o carpetas que consideres necesarios de acuerdo con las buenas prácticas de OpenAPI
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

**Agente:** Claude Code (Sonnet 5) - **Contexto:** El agente acaba de crear las HU y las ha agrupado por épica.

```
elige las 3 historias de usuario más relevantes y las copias al readme
```

---

### 6. Tickets de Trabajo

Los tres *prompts* más relevantes: creación inicial, refinamiento y una funcionalidad añadida de principio a fin. Todos los demás (tickets de cada épica, refinamientos e implementación) están, en orden, en [`docs/prompts-completos.md`](docs/prompts-completos.md).

**Prompt 1:** 3 tickets de arranque

**Agente:** Claude Code (Sonnet 5) - **Contexto:** Nos centramos en el arranque de la estructura técnica de desarrollo para el proyecto

```
Genera los siguientes tres tickets de desarrollo. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto.

- Ticket 1 - Infrastructura: Añade db a Docker Compose con PostgreSQL 16. Si no existe configuración de docker y/o docker compose, creala. La base de datos debe tener volumen persistente para salvar datos.
  
- Ticket 2 - Backend: Añade fastapi conforme a lo descrito en el proyecto, pero no implementes endpoints ni lógica de negocio. Sólo la estructura vacía. Añadelo también a docker y docker compose, con un volumen persistente para los assets.

- Ticket 3 - Frontend : Añade las configuraciones para el frontend, incluye lo necesario en docker y docker compose pero sin implementar todavía el código del frontend
```

**Prompt 2:** Refinement tickets Épicas 02 a 06

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

**Prompt 3:** Recuperación de la contraseña olvidada, de la épica a producción

**Agente:** Claude Code (Opus 5.5) - **Contexto:** La pantalla de inicio de sesión no ofrece ninguna salida a quien olvida su contraseña

```
En la pantalla de login, no hay enlace de "he olvidado mi contraseña", es necesario tenerlo. Crea una épica con sus historias de usuario y tickets para hacerlo. También debe quedar documentado como funcionalidad del MVP
```

```
implementa TK-100
```

**Nota**

El agente crea la Épica 14 con la HU-41 (pedir el enlace) y la HU-42 (elegir una contraseña nueva) y los tickets TK-100 a TK-105, de base de datos, backend, frontend y documentación. Después se implementa un ticket por *prompt* («implementa TK-1xx»): el agente encadena propuesta, implementación y archivo de OpenSpec y hace un commit por ticket. Tras desplegar, el recorrido completo se prueba en producción: pedir el enlace, cambiar la contraseña y recibir el aviso del cambio.

---


### 7. Pull Requests

**Prompt 1:** PR del MVP

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Completada la implementación de la primera versión funcional del MVP

```
Abre la PR hacia main
```

**Nota**

Al no tener el cliente de `gh` instalado con el token de seguridad configurado, Claude propone que la abra yo a mano. Me da el título y el contenido de la misma.

**Prompt 2:** PR de la segunda entrega

**Agente:** Claude Code (Opus 5.5) - **Contexto:** El proyecto está listo para la 2a entrega 

```
Haz git push y prepara una PR. No hagas la PR (gh client y el token necesario no están instalados). Sólo dame el título y el body de la PR para que yo la abra en Github
```

**Prompt 3:** PR de la producción en AWS

**Agente:** Claude Code (Opus 5.5) - **Contexto:** Implementados TK-078 a TK-089 (producción en AWS) en la rama de la tercera entrega

```
give me a PR description ready to copy in GH
```

**Nota**

El agente lista los commits pendientes de `main` y redacta título y descripción siguiendo la plantilla de *pull request* del repositorio, con el resultado de las comprobaciones y lo que ocurrirá al fusionar (despliegue continuo).
