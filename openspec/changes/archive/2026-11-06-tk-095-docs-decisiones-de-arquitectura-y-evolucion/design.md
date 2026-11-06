## Context

Las entradas de decisiones de TK-082 a TK-092 ya estaban en `infra/aws/README.md`; faltaban el resumen frente a lo previsto, las decisiones de red, secretos y DNS y la hoja de ruta.

## Goals / Non-Goals

**Goals:** un sitio único para entender cada diferencia y cuándo cambiarla.

**Non-Goals:** implementar pasos de evolución; ADR en ficheros separados.

## Decisions

- **Sección única en la guía, no ADR separados:** son pocas decisiones y viven junto a la operación; si crecen, se pasa a `docs/architecture/decisions/`.
- **Tabla resumen + entradas detalladas:** la tabla responde «qué y cuánto»; las entradas, «por qué y cuándo revisarlo», con el formato ya usado desde TK-082.
- **Protección web según lo desplegado:** el ticket suponía el plan gratuito de CloudFront con WAF; el plan del proyecto lo deniega (TK-087), así que la fila dice «sin WAF» y el paso 4 de evolución admite el plan de CloudFront (con el plan de pago) o una Web ACL.
- **El readme resume y enlaza:** tabla de cuatro columnas sin costes por fila; el detalle solo en la guía.

## Risks / Trade-offs

- **Cifras que envejecen:** llevan fecha y región, y se revisan al dar cada paso.
- **Señales asumidas:** se fijan con las métricas de TK-091 tras unas semanas en producción.
