## Context

La instancia (TK-085) publica solo el puerto 80 del proxy (TK-086), que exige `X-Origin-Verify`; su grupo de seguridad solo admite la lista de prefijos de CloudFront (TK-079). El certificado de ACM (`us-east-1`) de la raíz y `www` está emitido y la zona está en Route 53 (TK-084). El Compose ya fija `WEB_PUBLIC_URL` y `CORS_ORIGINS` en `https://entrevecinos.org`.

## Goals / Non-Goals

**Goals:** web en `https://entrevecinos.org` con `www` redirigido, estáticos en caché, límites de peticiones por IP y DDoS estándar, todo en Terraform y sin coste fijo.

**Non-Goals:** WAF (sin plan Free disponible y sin decisión de pagarlo), cifrado CloudFront → instancia (mejora documentada), orígenes VPC, Shield Advanced, alarmas (TK-091).

## Decisions

- **Sin plan Free ni WAF; límites en el proxy.** El proveedor `~> 6.70.0` tiene `aws_pricingplanmanager_subscription` y el `plan` lo aceptaba, pero el proyecto está en el plan FREE de AWS y su política de control de servicios deniega `pricingplanmanager:*` (`explicitDeny` en `CreateSubscription` y `ListSubscriptions`, también desde la consola). Decisión del proyecto: la alternativa del ticket, sin WAF de pago (≈ 10 USD/mes). Protección DDoS: Shield Standard de CloudFront, gratuito.
- **Límites por IP en nginx.** La IP del visitante es el último valor de `X-Forwarded-For`, que añade CloudFront; como solo CloudFront llega al origen (grupo de seguridad y cabecera), no se puede falsear. `limit_req`: 4 `POST` por minuto con ráfaga de 10 (≈ 20 en 5 minutos) a `/iniciar-sesion` y `/registro`, en una zona común, y 5 peticiones por segundo con ráfaga de 100 en general; responde `429` y lo registra (`warn`) en `/entrevecinos/prod/app/proxy`. El registro de accesos usa la IP del visitante. Sin reglas contra patrones maliciosos: la API valida las entradas y las consultas son parametrizadas. Como nginx lee la plantilla solo al arrancar y Compose no recrea un contenedor si solo cambia un fichero montado, `deploy.sh` exporta la huella de `prod/proxy/` (`PROXY_CONFIG_HASH`) y el Compose la pone en una etiqueta del proxy.
- **Módulo con un solo proveedor, el de `us-east-1`.** CloudFront y la fuente de registros de una distribución se gestionan desde `us-east-1` (excepción permitida para recursos globales). Route 53 es global.
- **Política de petición `AllViewer`, no `AllViewerExceptHostHeader`** como dice el ticket. Next.js compara `Origin` con `Host` (o `X-Forwarded-Host`) en las Server Actions; con `AllViewerExceptHostHeader` el `Host` sería el DNS de la instancia y las acciones fallarían. El origen es HTTP, así que reenviar el `Host` del visitante no rompe ningún certificado, y el proxy ya lo pasa a la web (`proxy_set_header Host $host`). Evita `serverActions.allowedOrigins` y reconstruir la imagen.
- **Caché:** `Managed-CachingDisabled` por defecto (HTML, RSC y Server Actions); `Managed-CachingOptimized` para `/_next/static/*` (nombres con *hash*). Sin política de cabeceras de respuesta: Next.js ya envía la CSP con *nonce*, HSTS y el resto, y CloudFront no las toca.
- **Redirección de `www` con CloudFront Function** (`cloudfront-js-2.0`, *viewer request*) en los dos comportamientos; reconstruye la *query* desde `request.querystring`. HTTP → HTTPS lo hace `redirect-to-https` antes.
- **Rutas reales:** `/iniciar-sesion` y `/registro` (el ticket dice `/login`).
- **Registros estándar v2** a `/entrevecinos/prod/cloudfront` en `us-east-1` (7 días, JSON).
- **`PriceClass_All`**: con el tráfico del MVP todo cabe en la capa gratuita permanente de CloudFront y Europa es una de las regiones más baratas.

## Risks / Trade-offs

- [Sin WAF, los ataques de capa 7 llegan a la instancia] → límites por IP en el proxy, CloudFront absorbe el volumen y Shield Standard la capa 3/4; revisar al subir de plan de AWS (el plan Free de CloudFront o una web ACL).
- [Los límites del proxy se aplican tras cruzar CloudFront y consumen CPU de la instancia] → aceptable con tráfico de MVP.
- [Tráfico CloudFront → instancia en HTTP] → mejora documentada en el ticket (origen HTTPS con certificado propio).
- [Superar la capa gratuita de CloudFront] → pago por uso; presupuesto y avisos de TK-078.
