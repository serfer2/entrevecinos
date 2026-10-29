## 1. Documentación

- [x] 1.1 Diagrama de `readme.md` §2.1: seguridad dentro de «FastAPI · Python» y cabeceras de Next.js en lugar de Helmet (TK-073 §3.1)
- [x] 1.2 Justificación de §2.1 y descripción de componentes de §2.2: sin «Capa de seguridad» ni Helmet
- [x] 1.3 §2.5: cabeceras de seguridad configuradas en Next.js y CSP con *nonce*
- [x] 1.4 Ningún otro texto de §1 a §5 habla de una capa de seguridad intermedia ni de Helmet

## 2. Verificación

- [x] 2.1 `grep -n -i "capa de seguridad" readme.md` sin resultados y `helmet` solo para decir que no se usa (§2.1, §2.5) y en los tickets copiados de §6
- [x] 2.2 Diagrama renderizado con `mermaid-cli`
- [ ] 2.3 Revisar la vista previa del `readme.md` en GitHub tras el push
