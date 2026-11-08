## Context

TK-098 llevó el correo a Brevo; SES se conserva como vuelta atrás con la identidad de prueba que creó TK-083 para el *sandbox*.

## Goals / Non-Goals

**Goals:** sin restos del *sandbox* y aviso del primer correo que no sale. **Non-Goals:** reintentos ni cambios en cómo envía la API.

## Decisions

- **Variable conservada, lista vacía:** `ses_test_recipients` sigue existiendo para volver a SES en *sandbox*; `prod.tfvars` (no versionado) la deja en `[]`.
- **Umbral de 1 fallo:** un solo correo perdido es un vecino que no puede activar su cuenta; con poco tráfico no hay ruido.
- **Rebotes fuera de la alarma:** el proveedor acepta el correo y rebota después; se ve en Brevo, no en la API.
- **AC1 con la evidencia de TK-098:** el registro de extremo a extremo con Gmail y Outlook (`dkim=pass`, `dmarc=pass`) ya se hizo el 2026-11-06 sobre la misma configuración.

## Risks / Trade-offs

- Un fallo transitorio del proveedor avisa aunque el vecino reenvíe con éxito; se acepta por el poco tráfico.
