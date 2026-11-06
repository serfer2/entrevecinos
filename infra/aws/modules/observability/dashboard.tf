# Panel de producción (TK-091). Está en eu-north-1; el gráfico de CloudFront lee us-east-1 (solo lectura).

data "aws_region" "current" {}

locals {
  region = data.aws_region.current.region

  graph = { for k, w in {
    cpu = {
      title = "Instancia: CPU (%) y créditos"
      metrics = [
        ["AWS/EC2", "CPUUtilization", "InstanceId", var.instance_id],
        ["AWS/EC2", "CPUCreditBalance", "InstanceId", var.instance_id, { yAxis = "right" }],
      ]
    }
    memory = {
      title = "Instancia: memoria y swap (%)"
      metrics = [
        ["CWAgent", "mem_used_percent", "InstanceId", var.instance_id],
        ["CWAgent", "swap_used_percent", "InstanceId", var.instance_id],
      ]
    }
    disks = {
      title = "Discos (%)"
      metrics = [
        ["CWAgent", "disk_used_percent", "InstanceId", var.instance_id, "path", "/", "fstype", "xfs"],
        ["CWAgent", "disk_used_percent", "InstanceId", var.instance_id, "path", var.postgres_mount, "fstype", "xfs"],
      ]
    }
    backups = {
      title   = "Copias correctas por hora"
      stat    = "Sum"
      period  = 3600
      metrics = [["Entrevecinos/Backup", "BackupSucceeded"]]
    }
    cloudfront = {
      title  = "CloudFront: peticiones y errores (%)"
      region = "us-east-1"
      metrics = [
        ["AWS/CloudFront", "Requests", "DistributionId", var.distribution_id, "Region", "Global", { stat = "Sum", yAxis = "right" }],
        ["AWS/CloudFront", "4xxErrorRate", "DistributionId", var.distribution_id, "Region", "Global"],
        ["AWS/CloudFront", "5xxErrorRate", "DistributionId", var.distribution_id, "Region", "Global"],
      ]
    }
    errors = {
      title = "Errores en los registros y rechazos 429 del proxy"
      stat  = "Sum"
      metrics = [
        [local.logs_namespace, "ApiErrors"],
        [local.logs_namespace, "DbErrors"],
        [local.logs_namespace, "Proxy5xx"],
        [local.logs_namespace, "RateLimited"],
        [local.logs_namespace, "EmailQuotaExceeded"],
        [local.logs_namespace, "EmailSendFailures"],
      ]
    }
    ses = {
      title = "SES: envíos y reputación"
      metrics = [
        ["AWS/SES", "Send", { stat = "Sum" }],
        ["AWS/SES", "Reputation.BounceRate", { yAxis = "right" }],
        ["AWS/SES", "Reputation.ComplaintRate", { yAxis = "right" }],
      ]
    }
    } : k => {
    type   = "metric"
    width  = 12
    height = 6
    properties = {
      title   = w.title
      region  = lookup(w, "region", local.region)
      view    = "timeSeries"
      stat    = lookup(w, "stat", "Average")
      period  = lookup(w, "period", 300)
      metrics = w.metrics
    }
  } }
}

resource "aws_cloudwatch_dashboard" "this" {
  dashboard_name = "entrevecinos-prod"
  dashboard_body = jsonencode({
    widgets = concat(
      [{
        type   = "alarm"
        width  = 24
        height = 4
        properties = {
          title  = "Alarmas"
          alarms = concat([for a in aws_cloudwatch_metric_alarm.this : a.arn], [aws_cloudwatch_metric_alarm.web_5xx.arn])
        }
      }],
      [for k in ["cpu", "memory", "disks", "backups", "cloudfront", "errors", "ses"] : local.graph[k]],
    )
  })
}
