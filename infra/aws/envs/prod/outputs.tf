output "vpc_id" {
  description = "VPC de producción."
  value       = module.network.vpc_id
}

output "public_subnet_id" {
  description = "Subred pública de la instancia."
  value       = module.network.public_subnet_id
}

output "app_security_group_id" {
  description = "Grupo de seguridad de la instancia."
  value       = module.network.app_security_group_id
}

output "ecr_repository_urls" {
  description = "Repositorios ECR de api y web."
  value       = module.storage.ecr_repository_urls
}

output "media_bucket" {
  description = "Bucket de imágenes (STORAGE_BUCKET)."
  value       = module.storage.media_bucket
}

output "media_public_origin" {
  description = "Origen de las URL prefirmadas (STORAGE_PUBLIC_URL de la web)."
  value       = module.storage.media_public_origin
}

output "postgres_volume_id" {
  description = "Volumen de datos de PostgreSQL."
  value       = module.database.volume_id
}

output "backups_bucket" {
  description = "Bucket de copias de pg_dump."
  value       = module.database.backups_bucket
}

output "ses_configuration_set" {
  description = "Configuration set de SES."
  value       = module.mail.configuration_set
}

output "name_servers" {
  description = "Servidores de nombres de Route 53 que se ponen en Dinahosting (TK-084)."
  value       = module.domain.name_servers
}

output "certificate_arn" {
  description = "Certificado HTTPS de entrevecinos.org y www (us-east-1)."
  value       = module.domain.certificate_arn
}

output "ses_domain_identity_arn" {
  description = "Identidad del dominio en SES."
  value       = module.mail.domain_identity_arn
}

output "instance_id" {
  description = "Instancia de aplicación (Session Manager y despliegue)."
  value       = module.compute.instance_id
}

output "instance_public_dns" {
  description = "DNS público de la instancia (origen de CloudFront, TK-087)."
  value       = module.compute.public_dns
}

output "deploy_document_name" {
  description = "Documento de SSM que despliega la aplicación (TK-086)."
  value       = module.compute.deploy_document_name
}

output "distribution_id" {
  description = "Distribución de CloudFront de la web (TK-087)."
  value       = module.edge.distribution_id
}

output "distribution_domain_name" {
  description = "Nombre *.cloudfront.net (pruebas antes del DNS)."
  value       = module.edge.distribution_domain_name
}

output "github_user" {
  description = "Usuario IAM de GitHub Actions (su clave, en el entorno production de GitHub, TK-088)."
  value       = module.ci.user_name
}

output "github_deploy_role_arn" {
  description = "Rol de despliegue de GitHub Actions (variable AWS_DEPLOY_ROLE_ARN)."
  value       = module.ci.deploy_role_arn
}

output "github_deploy_external_id" {
  description = "ExternalId del rol de despliegue (variable AWS_DEPLOY_ROLE_EXTERNAL_ID)."
  value       = module.ci.external_id
}

output "alerts_topic_arn" {
  description = "Tema SNS de los avisos; confirma la suscripción por correo (TK-091)."
  value       = module.observability.alerts_topic_arn
}
