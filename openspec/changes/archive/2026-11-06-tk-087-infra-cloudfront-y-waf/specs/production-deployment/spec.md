## ADDED Requirements

### Requirement: Límite de peticiones en el proxy
El proxy SHALL identificar al visitante por el último valor de `X-Forwarded-For` (el que añade CloudFront) y MUST responder `429` cuando una IP supera 20 peticiones `POST` en 5 minutos (con ráfaga de 10) a `/iniciar-sesion` y `/registro`, o 5 peticiones por segundo (con ráfaga de 100) en total. Los rechazos y el registro de accesos SHALL aparecer en `/entrevecinos/prod/app/proxy` con la IP del visitante.

#### Scenario: Fuerza bruta en el inicio de sesión
- **WHEN** envío desde una IP más de 11 `POST` seguidos a `/iniciar-sesion`
- **THEN** el proxy responde `429` y el rechazo aparece en `/entrevecinos/prod/app/proxy`

#### Scenario: X-Forwarded-For falseado
- **WHEN** el visitante envía su propio `X-Forwarded-For` con otra IP
- **THEN** el límite se aplica a la IP que añade CloudFront
