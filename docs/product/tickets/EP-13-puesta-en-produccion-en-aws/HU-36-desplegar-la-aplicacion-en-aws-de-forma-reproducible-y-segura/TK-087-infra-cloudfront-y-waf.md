# TK-087 · Infraestructura: CloudFront con HTTPS en `entrevecinos.org` y plan gratuito con WAF

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/edge/`, `infra/aws/envs/prod/`, variables de producción de la web y la API; registros de la web en la zona de Route 53 de TK-084 |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-084, TK-086 |
| **Referencias** | `readme.md` §2.4 («DNS + CDN + WAF, HTTPS»), §2.5 (cifrado del tráfico, CORS); `apps/web/next.config.ts` (HSTS en producción); `apps/web/src/features/auth/session.ts` (cookie `Secure`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La web se publica en `https://entrevecinos.org` con el certificado de ACM de TK-084; `www.entrevecinos.org` redirige a la raíz. El DNS está en Route 53 (TK-084): la raíz y `www` apuntan a CloudFront con registros **alias** `A` y `AAAA` que crea Terraform. CloudFront termina el HTTPS y reenvía a la instancia por HTTP, con la cabecera secreta que comprueba el proxy (TK-086); el grupo de seguridad ya solo admite el rango de CloudFront (TK-079).

La cookie de sesión es `Secure` en producción y Next.js envía HSTS, así que la web solo funciona por HTTPS. La API exige `WEB_PUBLIC_URL` en `https` en producción.

**Objetivo:** publicar la web en `https://entrevecinos.org` con CloudFront, protegerla con el WAF y la protección DDoS que incluye el **plan gratuito de tarifa plana de CloudFront** (coste 0, decisión de ahorro) y fijar las URL públicas de producción.

## 2. Alcance

**Incluye**
- Distribución CloudFront:
  - origen: DNS público de la instancia (TK-085), protocolo `http-only`, puerto 80, cabecera personalizada `X-Origin-Verify` con el valor de Parameter Store (TK-086);
  - comportamiento por defecto: `redirect-to-https`, métodos `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`, política de caché `CachingDisabled` y de petición `AllViewerExceptHostHeader` (cookies, *query* y cabeceras como `Next-Action` llegan al origen);
  - comportamiento `/_next/static/*`: `CachingOptimized` (ficheros con *hash*, caché larga);
  - política de cabeceras de respuesta: no sustituye las de Next.js (CSP con *nonce*, HSTS…); solo se añade si falta alguna (asumido);
  - nombres alternativos `entrevecinos.org` y `www.entrevecinos.org` con el certificado de ACM de TK-084 (SNI), `minimum_protocol_version = TLSv1.2_2021`, HTTP/2 y HTTP/3, compresión;
  - CloudFront Function en *viewer request* que responde `301` de `www.entrevecinos.org/<ruta>` a `https://entrevecinos.org/<ruta>`, conservando la *query*;
  - clase de precio y funciones compatibles con el plan de tarifa plana (comprobar al implementar si el plan fija la clase de precio o restringe alguna función, como CloudFront Functions o los registros de acceso);
  - registros estándar de acceso (v2) a CloudWatch Logs o a S3 con retención corta (asumido).
- **Plan de tarifa plana Free de CloudFront** asociado a la distribución (sin coste mensual, con un volumen de peticiones y de transferencia incluido al mes; según la documentación vigente al implementar). Incluye WAF y protección DDoS; se configura dentro de lo que permita el plan:
  - reglas gestionadas de AWS equivalentes a `AWSManagedRulesCommonRuleSet`, `KnownBadInputs` e `IpReputationList` (con la regla de tamaño del cuerpo excluida o en modo `count`, porque las Server Actions suben imágenes de hasta 6 MB);
  - límite de peticiones por IP, más estricto para `POST` a `/login` y `/registro` (asumido: 20 en 5 minutos), si el plan admite reglas de límite;
  - métricas de bloqueos en CloudWatch (`us-east-1`).
- **Comprobaciones previas** (paso 1 del plan de tareas): que el plan Free está disponible para el proyecto, que Terraform puede gestionarlo (si no, se asocia por consola o CLI y se documenta como paso manual en `infra/aws/README.md`), qué reglas de WAF permite y qué ocurre al superar el volumen incluido.
- **Alternativa si el plan no está disponible o no encaja:** sin WAF; límite de peticiones por IP en el proxy de TK-086 (Caddy con el módulo `caddy-ratelimit`, que exige una imagen propia con `xcaddy`, o nginx con `limit_req`) y la protección DDoS estándar de CloudFront, que es gratuita. **No** se contrata WAF por separado (≈ 6-10 USD/mes) sin decisión expresa del proyecto.
- Registros de la web en la zona de Route 53 (Terraform, sin pasos manuales):

  | Nombre | Tipo | Destino |
  |---|---|---|
  | `entrevecinos.org` | `A` y `AAAA` alias | la distribución (`domain_name` y `hosted_zone_id` de CloudFront) |
  | `www.entrevecinos.org` | `A` y `AAAA` alias | la misma distribución (la CloudFront Function redirige a la raíz) |

  `is_ipv6_enabled = true` en la distribución para que el `AAAA` responda. Los alias apuntan a la distribución por referencia: si se recrea, Terraform actualiza los registros en el mismo `apply`.
- Valores finales de producción, que se pasan a `deploy.sh` (TK-086): `WEB_PUBLIC_URL=https://entrevecinos.org`, `CORS_ORIGINS=https://entrevecinos.org`, `STORAGE_PUBLIC_URL` y `STORAGE_PUBLIC_ENDPOINT` con el origen del bucket.
- Prueba de extremo a extremo de HU-36 AC2.

**No incluye**
- Certificado de ACM y registros de correo (TK-084).
- Zona alojada de Route 53 y registros de correo y de políticas (TK-084).
- Shield Advanced (no disponible en el plan).

## 3. Requisitos técnicos

- El *body* de las Server Actions de publicación con imágenes llega hasta 6 MB (`next.config.ts`); el WAF de CloudFront solo inspecciona los primeros 16 KB por defecto, y la regla de tamaño del conjunto común bloquearía cuerpos de más de 8 KB: hay que excluirla o dejarla en `count`. Si el plan no permite ajustar esa regla, comprobar que la publicación con imágenes funciona antes de dar el ticket por terminado.
- Next.js necesita la cabecera `Host` original o `x-forwarded-host` coherente para las Server Actions (comprobación de origen): verificar que las acciones funcionan detrás de CloudFront y, si no, configurar `serverActions.allowedOrigins` con `entrevecinos.org`.
- CloudFront exige que el certificado de TK-084 esté emitido (y, por tanto, el dominio ya delegado en Route 53) antes de aceptar los nombres alternativos.
- Los registros alias no tienen TTL propio: la web responde en cuanto la distribución termina de desplegarse. Antes de crearlos se puede probar con la URL `*.cloudfront.net`.
- Los cambios de WAF y CloudFront tardan minutos en propagarse; el `apply` debe esperar (`wait_for_deployment = true`).

## 4. Criterios de aceptación

**AC1 — HTTPS (HU-36 AC2)**
- **Given** la distribución desplegada
- **When** abro `http://entrevecinos.org/` y `https://www.entrevecinos.org/login`
- **Then** el primero se redirige a `https://entrevecinos.org/`, el segundo a `https://entrevecinos.org/login`, y la respuesta incluye `Strict-Transport-Security` y la `Content-Security-Policy` de la web

**AC2 — Recorrido principal (HU-36 AC2)**
- **Given** la web en CloudFront
- **When** me registro con una dirección verificada en SES, valido el correo, inicio sesión, creo una comunidad, publico un anuncio con dos fotografías y abro su detalle
- **Then** todo funciona y las imágenes se cargan desde el bucket con URL prefirmadas sin violaciones de la CSP

**AC3 — Origen protegido (HU-36 AC3)**
- **Given** el DNS público de la instancia
- **When** lo pido directamente desde Internet
- **Then** la conexión no llega (grupo de seguridad) y, desde la propia instancia sin cabecera, el proxy responde `403`

**AC4 — WAF del plan gratuito**
- **Given** el plan Free asociado a la distribución (o, en su defecto, el límite de peticiones del proxy)
- **When** envío más peticiones `POST` a `/login` que el límite desde una IP, o una petición con un patrón malicioso conocido
- **Then** la petición se bloquea (`403` de CloudFront, o `429` del proxy en la alternativa) y aparece en las métricas o los registros, y la factura de CloudFront del mes es 0 USD

**AC5 — Estáticos en caché**
- **Given** una página cargada
- **When** pido de nuevo un fichero de `/_next/static/`
- **Then** la cabecera `x-cache` indica `Hit from cloudfront`, y las páginas HTML nunca se cachean

## 5. Plan de tareas

1. Comprobación del plan Free (disponibilidad, soporte en Terraform, reglas de WAF y límites).
2. Distribución con origen, comportamientos y políticas.
3. Asociación del plan Free y configuración de su WAF (o alternativa en el proxy).
4. Salidas y variables finales de producción; nuevo despliegue.
5. Ajustes de Server Actions y WAF tras la prueba de extremo a extremo.
6. Registros alias `A` y `AAAA` de la raíz y de `www` en Route 53.
7. Solicitud de salida del *sandbox* de SES (procedimiento de TK-083) con la URL ya disponible.

## 6. Verificación

```bash
make tf-apply
dig +short A entrevecinos.org && dig +short AAAA entrevecinos.org     # IP de CloudFront (v4 y v6)
dig +short A www.entrevecinos.org                                     # IP de CloudFront
curl -sI http://entrevecinos.org/ | head -3                        # 301 → https
curl -sI https://www.entrevecinos.org/login | grep -i '^location'   # https://entrevecinos.org/login
curl -sI https://entrevecinos.org/login | grep -i 'strict-transport\|content-security'
curl -sI https://entrevecinos.org/_next/static/<fichero> | grep -i x-cache
for i in $(seq 1 30); do curl -s -o /dev/null -w '%{http_code} ' -X POST https://entrevecinos.org/login; done
# Navegador: recorrido de AC2 con DevTools abiertas (Consola sin errores de CSP)
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `make tf-lint` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Orígenes VPC de CloudFront:** permiten que CloudFront llegue a una instancia en subred privada sin IP pública, eliminando la cabecera secreta y la exposición de la IP. Exige que la instancia salga a Internet por NAT (≈ 35 USD/mes) o endpoints de interfaz. Recomendado cuando el presupuesto lo permita; comprobar su disponibilidad en `eu-north-1`.
- **Límites del plan Free:** el volumen incluido es suficiente con poco tráfico; al crecer, el siguiente plan de tarifa plana tiene cuota mensual fija. Revisar el consumo en la consola de CloudFront y subir de plan cuando el proyecto escale.
- **WAF del plan más limitado que una Web ACL propia:** menos reglas y menos configuración. Aceptado por coste mientras el proyecto no escale.
- **Tráfico CloudFront → instancia sin cifrar:** viaja por la red de AWS e Internet en HTTP. Con el DNS en Route 53 ya se puede cifrar de forma automática: un nombre `origin.entrevecinos.org` (`A` a la IP elástica de la instancia) con un certificado de Let's Encrypt en Caddy por desafío DNS-01 (módulo `caddy-dns/route53`, permiso del rol limitado a esa zona) y origen `https-only`; añadir `letsencrypt.org` al `CAA` (TK-084). Se deja como mejora; el desafío HTTP-01 no sirve porque la instancia solo admite tráfico de CloudFront.
- **Dependencia del DNS de AWS:** web y DNS dependen de la misma cuenta; si se pausa el proyecto por el límite de gasto (TK-078), Route 53 puede dejar de servir la zona además de la web. Mantener el gasto lejos del límite (avisos de TK-078).
