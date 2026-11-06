# Métricas a partir de los registros de la aplicación (TK-091), en Entrevecinos/Logs.

locals {
  logs_namespace = "Entrevecinos/Logs"

  metric_filters = {
    # PostgreSQL: PANIC siempre; FATAL salvo los mensajes normales de un reinicio.
    db-panic = { group = "db", metric = "DbErrors", pattern = "PANIC" }
    db-fatal = {
      group   = "db"
      metric  = "DbErrors"
      pattern = "FATAL -\"administrator command\" -\"the database system is\""
    }
    # API: líneas ERROR de uvicorn y trazas de logger.exception (sin configuración de logging,
    # Python escribe el mensaje y la traza sin nivel).
    api-error     = { group = "api", metric = "ApiErrors", pattern = "\"ERROR:\"" }
    api-traceback = { group = "api", metric = "ApiErrors", pattern = "\"Traceback (most recent call last)\"" }
    # Cupo de correos por coste (TK-099): aviso al 80 % y cada envío bloqueado.
    email-quota-80       = { group = "api", metric = "EmailQuotaWarning", pattern = "\"Cupo de correo al 80\"" }
    email-quota-exceeded = { group = "api", metric = "EmailQuotaExceeded", pattern = "\"Límite mensual de correos alcanzado\"" }
    # Proxy: todas las peticiones y las 5xx (alarma web-5xx) y las rechazadas por límite (sustituyen a
    # los bloqueos del WAF; solo en el panel).
    proxy-requests = { group = "proxy", metric = "ProxyRequests", pattern = "[ip, time, request, status, ...]" }
    proxy-5xx      = { group = "proxy", metric = "Proxy5xx", pattern = "[ip, time, request, status = 5*, ...]" }
    proxy-429      = { group = "proxy", metric = "RateLimited", pattern = "[ip, time, request, status = 429, ...]" }
  }
}

resource "aws_cloudwatch_log_metric_filter" "this" {
  for_each = local.metric_filters

  name           = "entrevecinos-prod-${each.key}"
  log_group_name = "${var.log_group_prefix}/${each.value.group}"
  pattern        = each.value.pattern

  metric_transformation {
    name          = each.value.metric
    namespace     = local.logs_namespace
    value         = "1"
    default_value = "0"
  }
}
