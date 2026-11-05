output "zone_id" {
  description = "Zona alojada de Route 53."
  value       = aws_route53_zone.this.zone_id
}

output "name_servers" {
  description = "Servidores de nombres que se ponen en Dinahosting."
  value       = aws_route53_zone.this.name_servers
}

output "domain" {
  description = "Dominio de la zona."
  value       = var.domain
}

output "certificate_arn" {
  description = "Certificado de ACM (us-east-1) para CloudFront (TK-087)."
  value       = var.wait_for_certificate_validation ? aws_acm_certificate_validation.this[0].certificate_arn : aws_acm_certificate.this.arn
}
