## Context

Registro y reenvío envían el correo en segundo plano tras responder (`send_in_background`), con la sesión de base de datos de la petición: se confirma al terminar y se revierte si hay error.

## Goals / Non-Goals

**Goals:** tope de coste garantizado en la propia aplicación, sin carreras ni tareas programadas. **Non-Goals:** cupos por usuario o IP, cola de envíos diferidos, sincronizar con el contador de Brevo.

## Decisions

- **Restricción de costes:** 5.000 al mes es el plan más barato de Brevo (≈ 9 USD/mes), dentro del límite de 40 €/mes. Subirlo se decide con el presupuesto.
- **Periodo en el dominio** (`current_period`): función pura con la zona `Europe/Madrid` (asumido); fila por periodo identificada por la fecha local de inicio, así el contador nuevo empieza solo.
- **Reserva atómica en una sentencia:** `INSERT … ON CONFLICT (period_start) DO UPDATE SET sent = sent + 1 WHERE sent < :limit RETURNING sent`. Sin fila devuelta, no hay cupo. El bloqueo de fila de PostgreSQL serializa las peticiones concurrentes.
- **Misma transacción que la cuenta:** si el registro falla después (409), la plaza se revierte; si falla el envío en segundo plano, la plaza ya está consumida (criterio conservador).
- **Reenvío sin filtrar existencia:** comprueba el cupo (lectura) antes de buscar la cuenta; reserva solo si va a enviar.
- **Aviso del 80 % exacto:** como cada reserva devuelve un número distinto, solo una petición ve el umbral (`ceil(0,8 × límite)`) y el aviso sale una vez por periodo.
- **Registros como fuente de las alarmas:** mensajes fijos en español y filtros de métricas, como el resto de TK-091.

## Risks / Trade-offs

- **Denegación de servicio por agotamiento:** 5.000 registros falsos bloquean el registro hasta el día 6; lo frenan los límites por IP del proxy y las alarmas permiten reaccionar.
- **Zona horaria asumida:** con UTC, el corte cambiaría una o dos horas.
