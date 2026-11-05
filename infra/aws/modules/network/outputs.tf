output "vpc_id" {
  description = "ID de la VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_id" {
  description = "ID de la subred pública de la instancia."
  value       = aws_subnet.public.id
}

output "availability_zone" {
  description = "Zona de disponibilidad de la subred."
  value       = aws_subnet.public.availability_zone
}

output "app_security_group_id" {
  description = "Grupo de seguridad de la instancia de aplicación."
  value       = aws_security_group.app.id
}
