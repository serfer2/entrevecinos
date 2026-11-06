## 1. Documentación

- [x] 1.1 `readme.md` §2.4 (diagramas y texto) y §2.5; corrección de §2.2
- [x] 1.2 `infra/aws/README.md`: variables y salidas, «Runbook», costes y «Destruir el entorno»
- [x] 1.3 `infra/README.md`, `AGENTS.md` y `.env.example`

## 2. Verificación

- [x] 2.1 Diagramas renderizados con mermaid-cli 11.4.2 sin errores
- [x] 2.2 Comprobaciones del ticket: sin «Pendiente» en §2.4, decisión de coste en ambos ficheros, RDS y Secrets Manager solo como evolución o alternativa, sin secretos
- [x] 2.3 Revisión cruzada con los recursos reales (`make tf ARGS="state list"`) y de los comandos del *runbook* contra producción en modo lectura
