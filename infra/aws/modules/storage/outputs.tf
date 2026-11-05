output "ecr_repository_urls" {
  description = "URL de los repositorios ECR por servicio (api, web)."
  value       = { for name, repo in aws_ecr_repository.this : name => repo.repository_url }
}

output "ecr_repository_arns" {
  description = "ARN de los repositorios ECR por servicio (para los roles de TK-085 y TK-088)."
  value       = { for name, repo in aws_ecr_repository.this : name => repo.arn }
}

output "media_bucket" {
  description = "Nombre del bucket de imágenes (STORAGE_BUCKET)."
  value       = module.media_bucket.id
}

output "media_bucket_arn" {
  description = "ARN del bucket de imágenes."
  value       = module.media_bucket.arn
}

output "media_public_origin" {
  description = "Origen de las URL prefirmadas (STORAGE_PUBLIC_URL de la web, img-src de la CSP)."
  value       = "https://${module.media_bucket.regional_domain_name}"
}
