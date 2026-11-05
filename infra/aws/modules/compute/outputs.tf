output "instance_id" {
  description = "Instancia de aplicación (destino de Session Manager y de deploy.sh)."
  value       = aws_instance.app.id
}

output "public_dns" {
  description = "DNS público de la instancia: origen de CloudFront (TK-087)."
  value       = aws_instance.app.public_dns
}

output "role_arn" {
  description = "Rol de la instancia."
  value       = aws_iam_role.app.arn
}

output "role_policy_json" {
  description = "Política propia del rol (para validarla con IAM Access Analyzer)."
  value       = data.aws_iam_policy_document.app.json
}
