## ADDED Requirements

### Requirement: Contactar con el anunciante
El detalle SHALL ofrecer «Contactar con <nombre>», que muestra el teléfono (si existe, primero) como enlace `tel:` y el correo como enlace `mailto:` con el asunto «Interesado en: <título>»; al autor se le MUST mostrar «Este es tu anuncio.» en su lugar. A quien no es miembro aprobado no se le envían los datos de contacto.

#### Scenario: Sin teléfono
- **WHEN** el anunciante no tiene teléfono
- **THEN** al pulsar «Contactar» solo se ve su correo
