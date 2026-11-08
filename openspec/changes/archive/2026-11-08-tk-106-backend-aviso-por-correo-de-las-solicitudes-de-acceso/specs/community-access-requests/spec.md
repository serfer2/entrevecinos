## ADDED Requirements

### Requirement: Aviso por correo a la administración
Al crear una solicitud con `POST /v1/communities/{community_id}/memberships`, la API SHALL enviar en segundo plano un correo a cada miembro `approved` con rol `community_admin` de la comunidad cuya cuenta esté activa y no borrada, uno por destinatario. El correo SHALL tener el asunto «Nueva solicitud para unirse a {comunidad}», el nombre del solicitante y el enlace `{WEB_PUBLIC_URL}/comunidades/{community_id}/gestion/solicitudes`, y MUST NOT incluir el correo ni el teléfono del solicitante. Los miembros, moderadores y administradores no aprobados MUST NOT recibirlo. La respuesta del endpoint no cambia.

#### Scenario: Comunidad con dos administradores y un moderador
- **WHEN** un vecino solicita unirse
- **THEN** la respuesta es `201` y se envían dos correos, uno a cada administrador

#### Scenario: Solicitud repetida
- **WHEN** un vecino con una membresía en la comunidad vuelve a solicitarla
- **THEN** la respuesta es `409` y no se envía ningún correo

### Requirement: Cupo de los avisos de solicitud
Cada aviso SHALL consumir una plaza del cupo de correos del periodo. Sin cupo, la solicitud MUST crearse igual y no SHALL enviarse ningún aviso más.

#### Scenario: Sin cupo
- **WHEN** un vecino solicita unirse con el cupo agotado
- **THEN** la respuesta es `201`, la solicitud queda `pending` y no se envía ningún aviso
