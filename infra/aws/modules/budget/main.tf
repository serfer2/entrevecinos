# Presupuesto mensual igual al límite de gasto del proyecto (TK-078). Solo avisa: el freno real
# es el límite de gasto de AWS Settings, que pausa el proyecto al alcanzarse.

locals {
  actual_thresholds = [50, 75, 90]
}

resource "aws_budgets_budget" "monthly" {
  name         = "entrevecinos-mensual"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_limit_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  dynamic "notification" {
    for_each = local.actual_thresholds
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = notification.value
      threshold_type             = "PERCENTAGE"
      notification_type          = "ACTUAL"
      subscriber_email_addresses = [var.alert_email]
    }
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}
