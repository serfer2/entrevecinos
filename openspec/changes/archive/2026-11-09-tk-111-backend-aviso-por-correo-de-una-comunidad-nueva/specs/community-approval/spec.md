## ADDED Requirements

### Requirement: Aviso por correo de una comunidad nueva
Cuando `POST /v1/communities` crea una comunidad pendiente de aprobación, la API SHALL enviar en segundo plano un correo a cada `platform_admin` con la cuenta activa y no borrada, por separado, con el asunto «Nueva comunidad pendiente: {comunidad}», los datos de la comunidad (nombre, descripción, ciudad, código postal y fecha de creación), los del creador (nombre, correo, teléfono y fecha de alta) y el enlace `{WEB_PUBLIC_URL}/admin/comunidades#comunidad-{community_id}`. Una comunidad creada activa por un `platform_admin` MUST NOT generar aviso. Cada aviso SHALL consumir una plaza del cupo; sin cupo, la comunidad MUST crearse igual y no SHALL enviarse el aviso. La respuesta del endpoint no cambia.

#### Scenario: Comunidad de un vecino
- **WHEN** un vecino crea una comunidad y hay dos `platform_admin`
- **THEN** la respuesta es `201` y cada `platform_admin` recibe su propio «Nueva comunidad pendiente: {comunidad}» con los datos del creador y el enlace

#### Scenario: Comunidad de un platform_admin
- **WHEN** un `platform_admin` crea una comunidad
- **THEN** no se envía ningún aviso

#### Scenario: Sin cupo
- **WHEN** un vecino crea una comunidad con el cupo agotado
- **THEN** la respuesta es `201`, la comunidad queda pendiente y no se envía el aviso
