# Avisos por correo de las alarmas (TK-091). La suscripción queda pendiente hasta confirmarla. Solo en
# eu-north-1: la política de control de servicios del proyecto deniega SNS en us-east-1.

resource "aws_sns_topic" "alerts" {
  #checkov:skip=CKV_AWS_26:CloudWatch no publica en temas con la clave aws/sns; los avisos no llevan datos sensibles
  name = "entrevecinos-prod-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
