## Why

HU-36 AC2: la aplicación ya corre en la instancia (TK-086), pero solo se llega a ella desde dentro. Falta publicarla en `https://entrevecinos.org` con HTTPS, redirigir `www`, cachear los estáticos y limitar las peticiones por IP sin coste. El plan de tarifa plana Free de CloudFront (WAF incluido) no está disponible: la política de control de servicios del proyecto (plan FREE de AWS) deniega `pricingplanmanager:*`, así que se aplica la alternativa del ticket: sin WAF, con límites en el proxy y la protección DDoS estándar de CloudFront. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-087-infra-cloudfront-y-waf.md`.

## What Changes

- Módulo `infra/aws/modules/edge/` (nuevo, proveedor de `us-east-1`):
  - Distribución CloudFront con origen HTTP en la instancia y la cabecera `X-Origin-Verify`, `redirect-to-https`, HTTP/2 y HTTP/3, IPv6, TLS 1.2 mínimo, sin caché para páginas y Server Actions y con caché larga para `/_next/static/*`.
  - CloudFront Function que redirige `www.entrevecinos.org` a la raíz con `301`, conservando ruta y *query*.
  - Registros estándar de acceso (v2) en CloudWatch Logs (`us-east-1`, 7 días).
  - Alias `A` y `AAAA` de la raíz y de `www` en Route 53.
- `envs/prod`: módulo `edge` y salidas de la distribución.
- `infra/prod/proxy/default.conf.template`: IP del visitante desde `X-Forwarded-For` (último valor, el que añade CloudFront), `429` a más de 20 `POST` en 5 minutos por IP a `/iniciar-sesion` y `/registro`, límite general por IP y registro de accesos con la IP del visitante.
- Valores de producción de la web y la API (`WEB_PUBLIC_URL`, `CORS_ORIGINS`, `STORAGE_PUBLIC_URL`): ya fijados en el Compose de TK-086; se comprueban de extremo a extremo.

## Capabilities

### New Capabilities
- `aws-edge`: CloudFront, redirección de `www`, caché, registros de acceso y DNS de la web.

### Modified Capabilities
- `production-deployment`: el proxy limita las peticiones por IP del visitante.

## Impact

- Infraestructura: `infra/aws/modules/edge/`, `infra/aws/envs/prod/`, `infra/prod/proxy/` e `infra/aws/README.md` («Puesta en marcha», «Web pública», «Despliegue», «Operación», «Costes» y «Decisiones de arquitectura»). El cambio del proxy exige `make tf-apply` y un despliegue nuevo con los mismos *digests*.
- Sin cambios en la API, la web ni el Compose, salvo que la prueba de extremo a extremo lo exija (Server Actions o WAF).
- Coste: CloudFront con pago por uso, dentro de su capa gratuita permanente (1 TB y 10 millones de peticiones al mes) con tráfico de MVP; registros de acceso en CloudWatch Logs, céntimos al mes. Sin WAF (≈ 10 USD/mes).
