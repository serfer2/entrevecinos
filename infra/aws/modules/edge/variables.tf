variable "domain" {
  description = "Dominio de la web (TK-084); www.<dominio> redirige a él."
  type        = string
}

variable "zone_id" {
  description = "Zona de Route 53 del dominio (TK-084)."
  type        = string
}

variable "certificate_arn" {
  description = "Certificado de ACM en us-east-1 para el dominio y www (TK-084)."
  type        = string
}

variable "origin_domain_name" {
  description = "DNS público de la instancia (TK-085)."
  type        = string
}

variable "origin_verify" {
  description = "Valor de la cabecera X-Origin-Verify que exige el proxy de la instancia (TK-086)."
  type        = string
  sensitive   = true
}

variable "log_retention_days" {
  description = "Retención de los registros de acceso de CloudFront."
  type        = number
  default     = 7
}
