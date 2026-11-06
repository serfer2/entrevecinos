output "distribution_id" {
  description = "Distribución de CloudFront (invalidaciones y consola)."
  value       = aws_cloudfront_distribution.this.id
}

output "distribution_domain_name" {
  description = "Nombre *.cloudfront.net de la distribución."
  value       = aws_cloudfront_distribution.this.domain_name
}
