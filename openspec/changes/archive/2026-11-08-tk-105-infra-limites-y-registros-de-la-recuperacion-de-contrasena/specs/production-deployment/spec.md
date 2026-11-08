## MODIFIED Requirements

### Requirement: Límite de peticiones en el proxy
El proxy SHALL identificar al visitante por el último valor de `X-Forwarded-For` (el que añade CloudFront) y MUST responder `429` cuando una IP supera 20 peticiones `POST` en 5 minutos (con ráfaga de 10) entre `/iniciar-sesion`, `/registro`, `/recuperar-contrasena` y `/restablecer-contrasena`, o 5 peticiones por segundo (con ráfaga de 100) en total. Los rechazos y el registro de accesos SHALL aparecer en `/entrevecinos/prod/app/proxy` con la IP del visitante y sin la cadena de consulta.

#### Scenario: Fuerza bruta en el inicio de sesión
- **WHEN** envío desde una IP más de 11 `POST` seguidos a `/iniciar-sesion`
- **THEN** el proxy responde `429` y el rechazo aparece en `/entrevecinos/prod/app/proxy`

#### Scenario: Abuso del formulario de recuperación
- **WHEN** envío desde una IP más de 11 `POST` seguidos a `/recuperar-contrasena`
- **THEN** el proxy responde `429` y no se envían más correos

#### Scenario: Enlace de restablecimiento en los registros
- **WHEN** se abre un enlace `/restablecer-contrasena/enlace?token=…`
- **THEN** el registro del proxy muestra `/restablecer-contrasena/enlace` sin `token=`

#### Scenario: X-Forwarded-For falseado
- **WHEN** el visitante envía su propio `X-Forwarded-For` con otra IP
- **THEN** el límite se aplica a la IP que añade CloudFront
