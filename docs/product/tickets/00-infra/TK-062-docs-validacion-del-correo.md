# TK-062 · Documentación: validación del correo electrónico

| Campo | Valor |
|---|---|
| **Tipo** | Documentación |
| **Componente** | `readme.md`, `docs/product/user-stories.md`, `docs/api/README.md`, `infra/README.md`, `apps/api/README.md`, `apps/web/README.md` |
| **Historia** | HU-25 y HU-26 (Épica 10) |
| **Prioridad** | Media |
| **Depende de** | TK-056 a TK-061 |
| **Referencias** | Tickets de la Épica 10 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La Épica 10 cambia el registro (ya no inicia la sesión), añade un servicio de correo, variables de entorno, una tabla y endpoints. La documentación general no lo refleja.

**Objetivo:** dejar la documentación coherente con la validación del correo una vez implementada.

## 2. Alcance

**Incluye**
- `readme.md`:
  - MVP (§1.2, «Registro y perfil básico»): validación del correo por enlace con caducidad de 24 horas.
  - Arquitectura: servidor SMTP (Mailpit en desarrollo) en el diagrama y en la descripción de componentes.
  - Modelo de datos: `users.email_verified_at`, la restricción `ck_users_active_requires_verified_email` y la tabla `email_verification` (en el diagrama ER y en la descripción de tablas).
  - Instalación y variables de entorno: las de TK-056 y la URL de Mailpit (`http://localhost:8025`).
- `docs/product/user-stories.md`: HU-01 AC1 (el registro ya no deja la sesión iniciada; remite a HU-25) y HU-02 (no se puede iniciar sesión sin validar el correo).
- `docs/api/README.md`: comprobar las filas de «Cambios» de TK-058 y TK-059 y añadir los endpoints nuevos al resumen.
- `infra/README.md`: servicio `mail`, puertos y cómo ver los correos.
- `apps/api/README.md`: puerto `EmailSender`, adaptador SMTP y `FakeEmailSender` en las pruebas.
- `apps/web/README.md`: ruta `/verificar-correo` y flujo de registro.
- Aviso de actualización: los `.env` existentes necesitan las variables nuevas.

**No incluye**
- Las especificaciones de OpenSpec: se actualizan al archivar el cambio de cada ticket.
- Los propios tickets e historias, ya escritos.

## 3. Requisitos técnicos

- Mismo estilo y nivel de detalle que las secciones existentes; las inferencias se marcan `(asumido)`.
- Los diagramas Mermaid deben seguir siendo válidos.
- Nombres de variables, endpoints, tablas y mensajes copiados de la implementación final, no de los tickets.

## 4. Criterios de aceptación

**AC1 — Instalación desde cero**
- **Given** un clon nuevo del repositorio
- **When** sigo las instrucciones de instalación
- **Then** levanto el proyecto con el correo funcionando y sé dónde ver los correos de desarrollo

**AC2 — Coherencia**
- **Given** la documentación actualizada
- **When** la comparo con la implementación
- **Then** el flujo de registro, el modelo de datos, las variables y los endpoints coinciden

**AC3 — Historias**
- **Given** `user-stories.md`
- **When** leo HU-01 y HU-02
- **Then** no contradicen HU-25

## 5. Plan de tareas

1. `readme.md` (MVP, arquitectura, modelo de datos, instalación).
2. `user-stories.md` (HU-01, HU-02).
3. `docs/api/README.md`, `infra/README.md`, `apps/api/README.md`, `apps/web/README.md`.
4. Revisión cruzada con la implementación.

## 6. Verificación

```bash
grep -rn "email_verified_at\|Mailpit\|verificar-correo" readme.md docs infra apps/*/README.md
# Seguir las instrucciones de instalación en un clon limpio
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Diagramas Mermaid válidos.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- Ninguno relevante.
