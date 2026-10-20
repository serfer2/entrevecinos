# TK-039 · Frontend: contactar con el anunciante

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/components/ContactOwner.tsx`, detalle del anuncio, perfil) |
| **Historia** | HU-15 Contactar con el anunciante (Épica 5) |
| **Prioridad** | Alta |
| **Depende de** | TK-037, TK-038 |
| **Referencias** | `user-stories.md` HU-15 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-15 pide que, al elegir «Contactar», se muestren el teléfono y/o el correo del anunciante; el correo si no hay teléfono; y que nunca se muestren a quien no es miembro aprobado.

**Objetivo:** añadir la sección de contacto al detalle del anuncio.

## 2. Alcance

**Incluye**
- Componente `ContactOwner` en la sección del anunciante (TK-037).
- Enlaces `tel:` y `mailto:` (con asunto prellenado).
- Texto de ayuda del perfil ampliado al correo (TK-038 §8).

**No incluye**
- Mensajería interna, formularios de contacto o registro de contactos (post-MVP).

## 3. Requisitos técnicos

### 3.1 `ContactOwner`

- Botón «Contactar con <nombre>» que despliega (`<details>`/`<summary>` o botón con `aria-expanded`) los datos de contacto:
  - Teléfono, si existe: enlace `tel:<número sin espacios>` con el número formateado como lo escribió el anunciante.
  - Correo: enlace `mailto:<email>?subject=<"Interesado en: " + título>` (codificado con `encodeURIComponent`).
  - Orden: teléfono primero si existe (asumido: es el canal principal del MVP según el contrato).
- Si el anunciante soy yo, en lugar del botón se muestra «Este es tu anuncio.».
- Los datos llegan en el HTML del servidor solo porque la API ya los ha autorizado (TK-038); el desplegable es una cuestión de presentación, no de seguridad (asumido: ocultar en el cliente no protege nada, README §2.5).

### 3.2 Protección (HU-15 AC3)

- Las páginas que muestran anuncios solo existen para miembros aprobados: sin sesión, el proxy redirige (TK-009); sin membresía aprobada, la API responde `403` y la página muestra el aviso de acceso sin datos (TK-037).
- Prueba específica: el HTML devuelto a un usuario pendiente para `/anuncios/<id>` no contiene el correo ni el teléfono del anunciante.

### 3.3 Perfil

- Texto de ayuda del teléfono en `/perfil` (TK-011): «Opcional. Tu teléfono y tu correo los verán los vecinos de tus comunidades interesados en tus anuncios.».

### 3.4 Pruebas

- `ContactOwner`: con teléfono y correo, solo correo, propio anuncio; `href` de `tel:` y `mailto:` (codificación del asunto con tildes y `&`).
- Página: usuario pendiente no recibe datos de contacto.

## 4. Criterios de aceptación

**AC1 — Canal de contacto visible (HU-15 AC1)**
- **Given** que soy miembro aprobado y estoy en el detalle de un anuncio
- **When** pulso «Contactar con <nombre>»
- **Then** veo su teléfono y su correo como enlaces que abren el marcador y el correo con el asunto «Interesado en: <título>»

**AC2 — Anunciante sin teléfono (HU-15 AC2)**
- **Given** un anunciante sin teléfono
- **When** pulso «Contactar»
- **Then** veo solo su correo

**AC3 — Datos protegidos (HU-15 AC3)**
- **Given** que no he iniciado sesión o no soy miembro aprobado
- **When** intento abrir el anuncio
- **Then** no se me muestran sus datos de contacto (ni están en el HTML recibido)

## 5. Plan de tareas

1. `ContactOwner` y sus pruebas.
2. Integración en el detalle y texto del perfil.
3. Prueba de que el HTML para un no miembro no contiene datos de contacto; verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Miembro: detalle → «Contactar con …» → teléfono (tel:) y correo (mailto: con asunto)
# Anunciante sin teléfono → solo correo
# Pendiente: curl con su cookie a /anuncios/<id> | grep -c '<correo del anunciante>' → 0
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Recolección de contactos:** un miembro puede recorrer los anuncios y copiar los datos; aceptado en el MVP (comunidad cerrada con aprobación).
