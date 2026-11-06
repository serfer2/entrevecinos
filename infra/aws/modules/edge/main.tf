# Web pública en https://<dominio> con CloudFront (TK-087): HTTPS, redirección de www, caché de
# estáticos y alias en Route 53. Sin WAF: el plan del proyecto no admite el plan Free de CloudFront
# y el límite de peticiones lo pone el proxy de la instancia (infra/prod/proxy).
#
# Todo el módulo usa el proveedor de us-east-1: CloudFront y sus registros son globales y AWS los
# gestiona desde esa región.

data "aws_cloudfront_cache_policy" "disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_cache_policy" "optimized" {
  name = "Managed-CachingOptimized"
}

# Todo lo del visitante, incluida la cabecera Host: Next.js la compara con Origin en las Server
# Actions, y el origen es HTTP (no hay certificado que deba coincidir con el nombre).
data "aws_cloudfront_origin_request_policy" "all_viewer" {
  name = "Managed-AllViewer"
}

resource "aws_cloudfront_function" "www_redirect" {
  name    = "entrevecinos-www-redirect"
  comment = "301 de www.${var.domain} a ${var.domain}"
  runtime = "cloudfront-js-2.0"
  publish = true
  code    = templatefile("${path.module}/www-redirect.js", { domain = var.domain })
}

locals {
  origin_id = "instance"
}

resource "aws_cloudfront_distribution" "this" {
  #checkov:skip=CKV_AWS_86:registros estándar v2 a CloudWatch Logs (logs.tf); checkov solo ve los v1
  #checkov:skip=CKV_AWS_310:una sola instancia; no hay origen de respaldo
  #checkov:skip=CKV_AWS_374:sin restricción geográfica; la web es pública
  #checkov:skip=CKV2_AWS_32:Next.js envía la CSP con nonce, HSTS y el resto de cabeceras de seguridad
  #checkov:skip=CKV_AWS_68:sin WAF por coste; límite de peticiones en el proxy (README, «Decisiones»)
  #checkov:skip=CKV2_AWS_47:sin WAF por coste; límite de peticiones en el proxy
  #checkov:skip=CKV_AWS_305:la raíz la sirve Next.js; no hay objeto por defecto
  enabled         = true
  comment         = "EntreVecinos (TK-087)"
  aliases         = [var.domain, "www.${var.domain}"]
  is_ipv6_enabled = true
  http_version    = "http2and3"
  price_class     = "PriceClass_All"

  wait_for_deployment = true

  origin {
    origin_id   = local.origin_id
    domain_name = var.origin_domain_name

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = "X-Origin-Verify"
      value = var.origin_verify
    }
  }

  # Páginas, Server Actions y rutas de la web: nunca en caché.
  default_cache_behavior {
    target_origin_id         = local.origin_id
    viewer_protocol_policy   = "redirect-to-https"
    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    cache_policy_id          = data.aws_cloudfront_cache_policy.disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer.id
    compress                 = true

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.www_redirect.arn
    }
  }

  # Ficheros con hash en el nombre: caché larga en CloudFront.
  ordered_cache_behavior {
    path_pattern           = "/_next/static/*"
    target_origin_id       = local.origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
    compress               = true

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.www_redirect.arn
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

# Alias de la raíz y de www (sin TTL propio; siguen a la distribución si se recrea).
resource "aws_route53_record" "web" {
  for_each = {
    for pair in setproduct([var.domain, "www.${var.domain}"], ["A", "AAAA"]) :
    "${pair[0]}-${pair[1]}" => { name = pair[0], type = pair[1] }
  }

  zone_id = var.zone_id
  name    = each.value.name
  type    = each.value.type

  alias {
    name                   = aws_cloudfront_distribution.this.domain_name
    zone_id                = aws_cloudfront_distribution.this.hosted_zone_id
    evaluate_target_health = false
  }
}
