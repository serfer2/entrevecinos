## MODIFIED Requirements

### Requirement: Navegación privada
Las páginas privadas SHALL mostrar una cabecera con el logotipo «EntreVecinos», «Comunidades» (enlace a `/comunidades`) y «Mi perfil», con `aria-current="page"` en la sección actual, y un pie de página. La cabecera SHALL quedar fija desde `sm`.

#### Scenario: Sección actual
- **WHEN** el vecino está en `/perfil`
- **THEN** el enlace «Mi perfil» tiene `aria-current="page"`
