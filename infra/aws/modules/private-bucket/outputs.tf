output "id" {
  description = "Nombre del bucket."
  value       = aws_s3_bucket.this.id
}

output "arn" {
  description = "ARN del bucket."
  value       = aws_s3_bucket.this.arn
}

output "regional_domain_name" {
  description = "Nombre de dominio regional del bucket (origen de las URL prefirmadas)."
  value       = aws_s3_bucket.this.bucket_regional_domain_name
}
