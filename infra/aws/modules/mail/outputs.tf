output "configuration_set" {
  description = "Configuration set de SES (SES_CONFIGURATION_SET de la API)."
  value       = aws_sesv2_configuration_set.this.configuration_set_name
}

output "configuration_set_arn" {
  description = "ARN del configuration set (para la política del rol de la instancia, TK-085)."
  value       = aws_sesv2_configuration_set.this.arn
}

output "jwt_secret_parameter" {
  description = "Parámetro con el secreto de los JWT."
  value       = aws_ssm_parameter.jwt_secret.name
}

output "domain_identity_arn" {
  description = "Identidad del dominio en SES (para limitar ses:SendEmail en el rol de la instancia, TK-085)."
  value       = aws_sesv2_email_identity.domain.arn
}
