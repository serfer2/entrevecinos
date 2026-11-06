## MODIFIED Requirements

### Requirement: Anuncio no disponible o sin acceso
Si la API responde `404`, la página SHALL mostrar «Este anuncio no está disponible. Puede que se haya eliminado u ocultado.»; si responde `403`, «No tienes acceso a los anuncios de esta comunidad.».

#### Scenario: Eliminado
- **WHEN** se abre el enlace de un anuncio eliminado
- **THEN** se ve el mensaje de anuncio no disponible
