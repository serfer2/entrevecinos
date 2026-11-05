## Context

El remitente será `no-reply@entrevecinos.org`, que se verifica con DKIM en TK-084. SES empieza en *sandbox*.

## Goals / Non-Goals

**Goals:** SES preparado para medir y suprimir rebotes y quejas; secreto de los JWT fuera del repositorio y del estado.

**Non-Goals:** identidad del dominio (TK-084); alarmas (TK-091).

## Decisions

- **Parameter Store en lugar de Secrets Manager** (≈ 0,40 USD/secreto/mes): no se usaba la rotación gestionada.
- **`ephemeral` + `value_wo`:** el valor no se guarda en el estado; solo se escribe cuando sube `jwt_secret_version`.
- **TLS obligatorio** en el *configuration set* (`tls_policy = REQUIRE`).
- **Dimensión de CloudWatch** `app` (etiqueta del mensaje, por defecto `entrevecinos`) para las métricas de envío.

## Risks / Trade-offs

- [AWS puede denegar la salida del *sandbox*] → con dominio verificado (TK-084) es más probable; si no, solo reciben correo los destinatarios verificados.
- [Rotar el secreto invalida todas las sesiones] → procedimiento en «Secretos».
