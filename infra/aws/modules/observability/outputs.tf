output "alerts_topic_arn" {
  description = "Tema SNS de los avisos."
  value       = aws_sns_topic.alerts.arn
}

output "dashboard_name" {
  description = "Panel de CloudWatch de producción."
  value       = aws_cloudwatch_dashboard.this.dashboard_name
}
