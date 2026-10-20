# web-communities Specification

## Purpose
Pantallas de comunidades y navegación de la zona privada.
## Requirements
### Requirement: Crear una comunidad desde la interfaz
La página `/comunidades/nueva` SHALL mostrar un formulario (nombre, descripción, ciudad y código postal) que crea la comunidad y lleva a `/comunidades/<id>`, donde se muestra su nombre.

#### Scenario: Creación correcta
- **WHEN** el vecino escribe el nombre y pulsa «Crear comunidad»
- **THEN** llega a `/comunidades/<id>` con el nombre de la comunidad

### Requirement: Nombre obligatorio
El formulario MUST mostrar «El nombre de la comunidad es obligatorio.» sin llamar a la API cuando el nombre está vacío.

#### Scenario: Sin nombre
- **WHEN** se envía el formulario sin nombre
- **THEN** se ve el error bajo el campo y no hay llamada a la API

### Requirement: Navegación privada
Las páginas privadas SHALL mostrar una cabecera con «EntreVecinos», «Comunidades» y «Mi perfil», con `aria-current="page"` en la sección actual.

#### Scenario: Sección actual
- **WHEN** el vecino está en `/perfil`
- **THEN** el enlace «Mi perfil» tiene `aria-current="page"`

