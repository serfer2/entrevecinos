output "user_name" {
  description = "Usuario IAM cuya clave se guarda en el entorno production de GitHub."
  value       = aws_iam_user.github.name
}

output "deploy_role_arn" {
  description = "Rol que asume GitHub Actions (variable AWS_DEPLOY_ROLE_ARN)."
  value       = aws_iam_role.deploy.arn
}

output "external_id" {
  description = "ExternalId del rol (variable AWS_DEPLOY_ROLE_EXTERNAL_ID)."
  value       = var.external_id
}

output "deploy_policy_json" {
  description = "Política del rol (para validarla con IAM Access Analyzer)."
  value       = data.aws_iam_policy_document.deploy.json
}

output "user_policy_json" {
  description = "Política del usuario (para validarla con IAM Access Analyzer)."
  value       = data.aws_iam_policy_document.user.json
}
