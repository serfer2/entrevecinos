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

---

### 7. Pull Requests

**Prompt 1:**

**Prompt 2:**

**Prompt 3:**
