# Alarmas de producción (TK-091): avisan al entrar en ALARM y al volver a OK. Umbrales iniciales, a
# revisar tras unas semanas (README, «Observabilidad y alertas»). Runbook de cada una en el README.

locals {
  instance = { InstanceId = var.instance_id }

  alarms = {
    instance-down = {
      description = "Instancia caída: falla el status check de la instancia o del sistema"
      namespace   = "AWS/EC2", metric = "StatusCheckFailed", dimensions = local.instance
      statistic   = "Maximum", period = 60, periods = 2, operator = "GreaterThanOrEqualToThreshold"
      threshold   = 1, missing = "breaching"
    }
    cpu = {
      description = "CPU de la instancia por encima del 80 % durante 15 minutos"
      namespace   = "AWS/EC2", metric = "CPUUtilization", dimensions = local.instance
      statistic   = "Average", period = 300, periods = 3, operator = "GreaterThanThreshold"
      threshold   = 80, missing = "notBreaching"
    }
    cpu-credits = {
      description = "Quedan menos de 20 créditos de CPU: la instancia se limitará a su rendimiento base"
      namespace   = "AWS/EC2", metric = "CPUCreditBalance", dimensions = local.instance
      statistic   = "Minimum", period = 300, periods = 1, operator = "LessThanThreshold"
      threshold   = 20, missing = "notBreaching"
    }
    memory = {
      description = "Memoria de la instancia por encima del 85 % durante 10 minutos"
      namespace   = "CWAgent", metric = "mem_used_percent", dimensions = local.instance
      statistic   = "Average", period = 300, periods = 2, operator = "GreaterThanThreshold"
      threshold   = 85, missing = "notBreaching"
    }
    disk-root = {
      description = "Disco raíz por encima del 80 %"
      namespace   = "CWAgent", metric = "disk_used_percent"
      dimensions  = merge(local.instance, { path = "/", fstype = "xfs" })
      statistic   = "Maximum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 80, missing = "notBreaching"
    }
    disk-data = {
      description = "Volumen de datos de PostgreSQL por encima del 75 %"
      namespace   = "CWAgent", metric = "disk_used_percent"
      dimensions  = merge(local.instance, { path = var.postgres_mount, fstype = "xfs" })
      statistic   = "Maximum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 75, missing = "notBreaching"
    }
    # Una copia cada 6 horas: 7 horas seguidas sin dato solo ocurren si falta una (TK-082).
    backup-missing = {
      description = "Copia de la base de datos ausente: ninguna copia correcta en 7 horas"
      namespace   = "Entrevecinos/Backup", metric = "BackupSucceeded", dimensions = {}
      statistic   = "Sum", period = 3600, periods = 7, operator = "LessThanThreshold"
      threshold   = 1, missing = "breaching"
    }
    db-errors = {
      description = "Errores FATAL o PANIC de PostgreSQL en /entrevecinos/prod/app/db"
      namespace   = local.logs_namespace, metric = "DbErrors", dimensions = {}
      statistic   = "Sum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 0, missing = "notBreaching"
    }
    api-errors = {
      description = "Más de 10 errores de la API en 5 minutos en /entrevecinos/prod/app/api"
      namespace   = local.logs_namespace, metric = "ApiErrors", dimensions = {}
      statistic   = "Sum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 10, missing = "notBreaching"
    }
    # Cupo de correos por coste (TK-099): aviso al cruzar el 80 % y en cada envío bloqueado.
    email-quota-80 = {
      description = "Se ha usado el 80 % del cupo de correos del periodo (límite por coste)"
      namespace   = local.logs_namespace, metric = "EmailQuotaWarning", dimensions = {}
      statistic   = "Sum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 0, missing = "notBreaching"
    }
    email-quota-exceeded = {
      description = "Cupo de correos agotado: el registro y el reenvío responden 503 hasta el día 6"
      namespace   = local.logs_namespace, metric = "EmailQuotaExceeded", dimensions = {}
      statistic   = "Sum", period = 300, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 0, missing = "notBreaching"
    }
    ses-bounces = {
      description = "Tasa de rebotes de SES por encima del 5 % (AWS revisa la cuenta a partir del 5 %)"
      namespace   = "AWS/SES", metric = "Reputation.BounceRate", dimensions = {}
      statistic   = "Maximum", period = 900, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 0.05, missing = "notBreaching"
    }
    ses-complaints = {
      description = "Tasa de quejas de SES por encima del 0,1 %"
      namespace   = "AWS/SES", metric = "Reputation.ComplaintRate", dimensions = {}
      statistic   = "Maximum", period = 900, periods = 1, operator = "GreaterThanThreshold"
      threshold   = 0.001, missing = "notBreaching"
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "this" {
  for_each = local.alarms

  alarm_name          = "entrevecinos-prod-${each.key}"
  alarm_description   = each.value.description
  namespace           = each.value.namespace
  metric_name         = each.value.metric
  dimensions          = each.value.dimensions
  statistic           = each.value.statistic
  period              = each.value.period
  evaluation_periods  = each.value.periods
  datapoints_to_alarm = each.value.periods
  comparison_operator = each.value.operator
  threshold           = each.value.threshold
  treat_missing_data  = each.value.missing
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

# Errores de la web: tasa de 5xx en el registro del proxy, con al menos 10 peticiones en 5 minutos para
# no saltar por un solo error. Las métricas de CloudFront solo existen en us-east-1, donde el proyecto
# no puede crear el tema SNS de los avisos.
resource "aws_cloudwatch_metric_alarm" "web_5xx" {
  alarm_name          = "entrevecinos-prod-web-5xx"
  alarm_description   = "Más del 5 % de las peticiones a la web terminan en 5xx durante 5 minutos (con 10 o más)"
  evaluation_periods  = 1
  comparison_operator = "GreaterThanThreshold"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  metric_query {
    id          = "rate"
    expression  = "IF(requests >= 10, 100 * errors / requests, 0)"
    label       = "5xx (%)"
    return_data = true
  }

  metric_query {
    id = "requests"
    metric {
      namespace   = local.logs_namespace
      metric_name = "ProxyRequests"
      stat        = "Sum"
      period      = 300
    }
  }

  metric_query {
    id = "errors"
    metric {
      namespace   = local.logs_namespace
      metric_name = "Proxy5xx"
      stat        = "Sum"
      period      = 300
    }
  }
}
