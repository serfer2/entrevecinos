## Context

El proxy aplica `zone=auth` (4 `POST` por minuto con ráfaga de 10, por la IP real del visitante) en un `location` regex de las páginas cuyas Server Actions hacen `POST` a su propia ruta. Los `GET` no cuentan porque la clave del mapa es vacía para ellos.

## Goals / Non-Goals

**Goals:** limitar el abuso del formulario de recuperación (correos a terceros, consumo del cupo) y la prueba de *tokens*; documentar la funcionalidad en la guía.

**Non-Goals:** alarmas nuevas (los fallos de envío y el cupo ya avisan); WAF.

## Decisions

- **Misma zona `auth`:** es el mismo tipo de abuso (formularios de autenticación). Compartirla significa que quien abusa de una ruta queda limitado también en las otras unos minutos; se acepta.
- **`/restablecer-contrasena/enlace` fuera del `location` exacto:** el regex termina en `$` y la ruta del enlace solo hace `GET`, que no consume la zona `auth` en ningún caso.
- **Valor explícito en el Compose:** `PASSWORD_RESET_TTL_MINUTES` ya vale 60 por defecto, pero se fija junto al resto de ajustes del correo para que el valor de producción se lea en un solo sitio.

## Risks / Trade-offs

- [Una IP compartida (oficina, NAT de un operador) con muchos vecinos legítimos puede recibir `429`] → mismo riesgo que hoy en el inicio de sesión; la ráfaga de 10 lo amortigua.
